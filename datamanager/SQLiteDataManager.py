from .data_manager_interface import DataManagerInterface
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from data.data_models import db, User, UserMovie, Movie
from sqlalchemy.exc import IntegrityError


class SQLiteDataManager(DataManagerInterface):
    # def __init__(self, db):
    #     self.db = db

    def list_all_users(self):
        # Return all users
        users = db.session.query(User).all()
        return users

    def list_user_movies(self, user_id):
        """
        Return all the movies for a given user

        :param: user_id
        :return: dictionary of movies
        """
        return db.session.query(UserMovie.imdb_id, UserMovie.user_rating, UserMovie.user_review, Movie.title,
                                Movie.genre, Movie.year, Movie.director, Movie.imdb_rating, Movie.img_url)\
            .join(Movie).filter(UserMovie.user_id == user_id).all()

    def get_user(self, user_id):
        """
        :param: user_id
        :return: user.name
        """
        return db.session.query(User).filter(User.id == user_id).one()

    def get_user_movie(self, user_id, imdb_id):
        return db.session.query(UserMovie, Movie) \
            .join(Movie, and_(UserMovie.user_id == user_id, UserMovie.imdb_id == imdb_id, Movie.imdb_id == imdb_id)) \
            .first()

    def get_user_imdb_ids(self, user_id):
        return db.session.query(UserMovie).with_entities(UserMovie.user_id, UserMovie.imdb_id) \
            .filter(UserMovie.user_id == user_id).all()

    def add_user(self, user):
        """
        :param: user object
        :return: user_name
        """
        db.session.add(user)
        db.session.commit()

    def add_user_movie(self, user_movie):
        """
        add a new user movie record
        :param: user movie object
        :return:
        """
        try:
            db.session.add(user_movie)
            db.session.commit()
            return f"Movie IMDB_ID {user_movie.imdb_id} added to favourites."
        except IntegrityError as e:
            db.session.rollback()
            return f"Movie IMDB_ID {user_movie.imdb_id} not added, movie already in User Favourites."

    def add_movie(self, movie):
        """
        add a new movie record
        :param: movie object
        :return:
        """
        try:
            db.session.add(movie)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()

    def update_movie(self, user_movie):
        """
        update user movies
        :param: user_movie object
        :return:
        """
        return True

    def delete_movie(self, user_movie):
        """
        deletes user movie record
        :param: user_movie object
        :return:
        """
        db.session.delete(user_movie)
        db.session.commit()

    def get_movie(self, imdb_id):
        return db.session.query(Movie).filter(Movie.imdb_id == imdb_id).first()

