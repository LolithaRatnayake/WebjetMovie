from abc import ABC, abstractmethod
import configparser
import requests
import json
from custom_exception import ServerSideError


class BaseAdaptor(ABC):
    """
    This class contian common functionality between different providers
    Though this example contains same pattern for both endpoints there may be instances where it's not the same
    Hence different implementations for both below abstract methods
    """

    def __init__(self):
        self.config = configparser.ConfigParser()
        conf_found = self.config.read('config.ini')
        if len(conf_found) != 1:
            # Reraising issue as this is mandatory field for the object
            raise ServerSideError('Configuration loading failed', 'configuration file is missing')
        try:
            self.access_token = self.config.get('Auth', 'access_token')
        except configparser.NoSectionError:
            # Reraising issue as this is mandatory field for the object
            raise ServerSideError('Malformed Config file', 'Auth Section was missing')
        except configparser.NoOptionError:
            # Reraising issue as this is mandatory field for the object
            raise ServerSideError('Malformed Config file', 'access_token option was missing')

    def query_web_endpoint(self, url):
        headers = {'x-access-token': self.access_token}
        try:
            # Connection timeout is set to 3.05 as per standard. Readtimeout is set to accomodate server load delay
            response = requests.get(url, headers=headers, timeout=(3.05, 27))

        except requests.exceptions.RequestException:
            raise ServerSideError('Backend connection Error', f'connecting to {url} failed')

        status = response.status_code
        if status == 403:
            raise ServerSideError('Invalid accesstoken', f'Invalid accesstoken {self.access_token} for {url}')
        elif status == 404:
            raise ServerSideError('Invalid Url', f'Invalid url {url}')
        elif status in (503, 500):
            raise ServerSideError('Service Unavailable', f'Service unavailable for {url}')
        elif status != 200:
            raise ServerSideError('Unknown error', f'Unknown Error connecting {url}. Received status {status}')

        return json.loads(response.content)

    @abstractmethod
    def get_movie_list(self):
        """
        This function returns a list of movies available at each provider
        :return: List of movies from the provider
        """
        pass

    @abstractmethod
    def get_movie(self, id):
        """
        This gets details of a movie
        :param id: unique ID of the movie
        :return: details of the movie
        """
        pass

    @property
    @abstractmethod
    def logo(self):
        """
        This return logo image
        This is property than instance/class variable as different endpoints may choose to provide logo differently.
        For example one endpoint may provide logo by their website and some, such as in our example, may get location
            from config file. So in this property method we can implement logic for each adaptor
        This contains default logo if they choose not to implement
        :return: logo image location
        """
        return '/static/webjet.png'


class CinemaWorld(BaseAdaptor):
    """
    This is a reqpresentation of Cinemaworld endpoint
    """

    def get_movie_list(self):
        """
        In different endpoints there might be different responses. In this case the returning object is filtered by
        "Movies" tag
        :return: Return list of movies.
        """
        resp = self.query_web_endpoint('http://webjetapitest.azurewebsites.net/api/cinemaworld/movies')
        return resp["Movies"]

    def get_movie(self, id):
        """
        In different endpoints the way url is formed may be different. Hence this seperate implementation
        :param id: instance Id which needs to be query
        :return: instance details
        """
        resp = self.query_web_endpoint(f'http://webjetapitest.azurewebsites.net/api/cinemaworld/movie/{id}')
        return resp

    @property
    def logo(self):
        """
        Logo location is taken from config file
        :return: logo location
        """

        try:
            logo = self.config.get('CinemaWorld', 'logo')
        except configparser.NoSectionError:
            # Reraising issue as this is mandatory field for the object
            raise ServerSideError('Malformed Config file', 'CinemaWorld Section was missing')
        except configparser.NoOptionError:
            # Reraising issue as this is mandatory field for the object
            raise ServerSideError('Malformed Config file', 'logo option was missing')
        return logo


class FilmWorld(BaseAdaptor):
    """
        This is a reqpresentation of Filmworld endpoint
    """

    def get_movie_list(self):
        """
        In different endpoints there might be different responses. In this case the returning object is filtered by
        "Movies" tag
        Mandatory fields in instance details: Title, Poster, ID
        :return: Return list of movies.
        """
        resp = self.query_web_endpoint('http://webjetapitest.azurewebsites.net/api/filmworld/movies')
        return resp["Movies"]

    def get_movie(self, movie_id):
        """
        In different endpoints the way url is formed may be different. Hence this seperate implementation
        Mandatory fields in instance details: Price, Poster, ID
        :param movie_id: instance Id which needs to be query
        :return: instance details
        """
        resp = self.query_web_endpoint(f'http://webjetapitest.azurewebsites.net/api/filmworld/movie/{movie_id}')
        return resp

    @property
    def logo(self):
        """
        Logo location is taken from config file
        :return: logo location
        """

        try:
            logo = self.config.get('FilmWorld', 'logo')
        except configparser.NoSectionError:
            # Reraising issue as this is mandatory field for the object
            raise ServerSideError('Malformed Config file', 'FilmWorld Section was missing')
        except configparser.NoOptionError:
            # Reraising issue as this is mandatory field for the object
            raise ServerSideError('Malformed Config file', 'logo option was missing')
        return logo
