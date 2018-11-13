from adaptors import CinemaWorld, FilmWorld
from custom_exception import ServerSideError
import traceback


class MovieFacade:
    """
    This is a Facade interface to collaborate between adaptors
    """
    def __init__(self, logger):
        self.logger = logger
        adaptor_list = [CinemaWorld, FilmWorld]
        self.instance_list = []
        for adaptor in adaptor_list:
            try:
                temp = adaptor()
                self.instance_list.append(temp)
            except ServerSideError as e:
                # If config parsing failed rather than failing all, just move on to the next instance
                self.logger.error(e.log_error_string + traceback.format_exc())

    def get_movies(self):
        """
        This query all the instances and stack up movies with presentable instance representation in custom
        data structure
        :return: list of all available movies
        """
        movies = dict()

        for endpoint_instance in self.instance_list:
            try:
                endpoint_offer = endpoint_instance.get_movie_list()
            except ServerSideError as e:
                self.logger.error(e.log_error_string + traceback.format_exc())
                continue
            index = endpoint_instance.__class__.__name__
            for movie in endpoint_offer:
                try:
                    title = movie['Title']
                    movie_id = movie['ID']
                    poster = movie['Poster']
                except KeyError:
                    self.logger.error(e.log_error_string + traceback.format_exc())
                    continue

                # This is combination of adaptor class name and movie id. Used to create link to movie
                instance_ref = f'{index}={movie_id}'

                if title in movies:
                    movies[title]['instance'].append(instance_ref)
                else:
                    movies[title] = {
                                        'title': title,
                                        'instance': [instance_ref],
                                        'poster': poster
                                        }
        # At this stage all the movies from all adaptors are recoreded so convert dictionary to list and return
        return movies.values()

    def movie_details(self, unique_id):
        """
        This function takes dictionary which has class names as Keys and their respective Id of the movie as value
        and returns details of the movie recorded in the systems
        :param unique_id_dictionary: {'AdaptorClassName': id, 'AdaptorClassName2': id2}
        :return: {'AdaptorClassName': detailobj}
        """
        lowest_price = None

        instance_list = []

        for instance in self.instance_list:
            classname = instance.__class__.__name__
            if classname in unique_id:  # Checks if this instance is requested
                try:
                    movie_detail = instance.get_movie(unique_id[classname])

                    movie_instance = {
                                      'logo': instance.logo,
                                      'poster': movie_detail.pop('Poster'),
                                      'ID': movie_detail.pop('ID'),
                                      'detail': movie_detail
                                      }

                    movie_price = float(movie_detail['Price'])
                except (ServerSideError, KeyError) as e:
                    self.logger.error(e.log_error_string + traceback.format_exc())
                    continue

                # Checks for lowest price
                if lowest_price:
                    if lowest_price > movie_price:
                        lowest_price = movie_price
                else:
                    lowest_price = movie_price

                instance_list.append(movie_instance)

        # mark whether instance has lowest price or not
        if lowest_price:
            for instance in instance_list:
                if lowest_price == float(instance['detail']['Price']):
                    instance['lowest'] = True
                else:
                    instance['lowest'] = False

        return instance_list
