from flask import Flask, request, render_template
from movie_facade import MovieFacade
from logging import FileHandler, INFO


app = Flask(__name__)

movie_fac = MovieFacade(app.logger)


@app.route('/')
def home():
    movie_list = movie_fac.get_movies()
    return render_template('home.html', movie_list=movie_list)

@app.route('/movie')
def movie():
    instance_id = request.args
    movie_details = movie_fac.movie_details(instance_id)
    return render_template('movie.html', instance_list=movie_details)


if __name__ == '__main__':
    log_handler = FileHandler('WebJetMovies.log')
    log_handler.setLevel(INFO)
    app.logger.addHandler(log_handler)
    app.run(debug=True)
