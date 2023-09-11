from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()


@dataclass
class User(db.Model):
    __tablename__ = 'users'

    id: int
    name: str

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(250), nullable=False)

    def __str__(self):
        return f"User(id = {self.id}, name = {self.name})"


@dataclass
class Movie(db.Model):
    __tablename__ = 'movies'

    imdb_id: str
    title: str
    genre: str
    year: int
    director: str
    imdb_rating: float
    img_url: str

    imdb_id = db.Column("imdb_id", db.String(9), primary_key=True)
    title = db.Column("title", db.String(250), nullable=False)
    genre = db.Column("genre", db.String(100))
    year = db.Column("year", db.Integer)
    director = db.Column("director", db.String(100))
    imdb_rating = db.Column("imdb_rating", db.Float)
    img_url = db.Column("img_url", db.String(100))

    def __str__(self):
        return f"Movie(imdb_id = {self.imdb_id}, title = {self.title}, " \
               f"genre = {self.genre}, year = {self.year}, director = {self.director}, " \
               f"imdb_rating = {self.imdb_id}, img_url = {self.img_url})"


@dataclass
class UserMovie(db.Model):
    __tablename__ = 'user_movies'

    user_id: int
    imdb_id: str
    user_rating: float
    user_review: str

    user_id = db.Column("user_id", db.Integer, db.ForeignKey('users.id'), primary_key=True)
    imdb_id = db.Column("imdb_id", db.String(9), db.ForeignKey('movies.imdb_id'), primary_key=True)
    user_rating = db.Column("user_rating", db.Float)
    user_review = db.Column("user_review", db.String(100))

    def add_user_movie(self):
        try:
            db.session.add(self)
            db.session.commit()
            return f"Movie IMDB_ID {self.imdb_id} added to favourites."
        except IntegrityError as e:
            db.session.rollback()
            return f"Movie IMDB_ID {self.imdb_id} not added, movie already in User Favourites."

    def delete_user_movie(self):
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        return f"User Movie(user_id = {self.user_id}, imdb_id = {self.imdb_id}, " \
               f"user_rating = {self.user_rating}, user_review = {self.user_review})"
