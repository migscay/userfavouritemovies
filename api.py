from flask import Blueprint, jsonify
from data.data_models import db, User, UserMovie, Movie
from datamanager.SQLiteDataManager import SQLiteDataManager
from imdb_api import fetch_data

api = Blueprint('api', __name__)

data_manager = SQLiteDataManager()


@api.route('/users', methods=['GET'])
def get_users():
    return jsonify(data_manager.list_all_users())


@api.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    movies = data_manager.list_user_movies(user_id)
    user = data_manager.get_user(user_id)

    # convert list of movies into dictionary
    movie_list = []
    for movie in movies:
        movie_details = {
            'imdb_id': movie.imdb_id,
             'user_rating': movie.user_rating,
             'user_review': movie.user_review,
             'title': movie.title,
             'genre': movie.genre,
             'year': movie.year,
             'director': movie.director,
             'imdb_rating': movie.imdb_rating,
             'img_url': movie.img_url
        }

        movie_list.append(movie_details)

    user_dict = {
        'id': user_id,
        'name': user.name,
        'movies': movie_list
    }

    return jsonify(user_dict)


@api.route('/users/<int:user_id>/movies/<imdb_id>', methods=['POST'])
def add_movie_to_user_movies(user_id, imdb_id):
    movie_data = fetch_data(imdb_id)
    movie = Movie(
        imdb_id=imdb_id,
        title=movie_data['Title'],
        genre=movie_data['Genre'],
        year=movie_data['Year'],
        director=movie_data['Director'],
        imdb_rating=movie_data['imdbRating'],
        img_url=movie_data['Poster']
    )
    data_manager.add_movie(movie)

    user_movie = UserMovie(
        user_id=user_id,
        imdb_id=imdb_id,
        user_rating=0,
        user_review=""
    )

    message = data_manager.add_user_movie(user_movie)
    movie = data_manager.get_movie(imdb_id)
    return jsonify(
        message=message,
        movie=movie
    )
