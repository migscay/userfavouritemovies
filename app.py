from flask import Flask, render_template, request, redirect, url_for, flash
from datamanager.SQLiteDataManager import SQLiteDataManager
from forms import UpdateMovieForm, AddUserForm
from data.data_models import db, User, UserMovie, Movie
from flask_bootstrap import Bootstrap
from w3lib.url import url_query_parameter
from imdb_api import search_req, fetch_data
from api import api
import os


app = Flask(__name__)
app.json.sort_keys = False
app.register_blueprint(api, url_prefix='/api')
bootstrap = Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# localhost and codio deploy
file_path = os.path.abspath(os.getcwd())+"/data/user_movies.sqlite"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
# pythonanywhere deploy
# data_folder = os.path.expanduser('~/mysite/data')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(data_folder, 'user_movies.sqlite')

db.init_app(app)

data_manager = SQLiteDataManager()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/users')
def list_users():
    users = data_manager.list_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def list_user_movies(user_id):
    movies = data_manager.list_user_movies(user_id)
    user = data_manager.get_user(user_id)
    return render_template('user-movies.html', user_id=user_id, user_name=user.name, movies=movies)


@app.route('/search_movie/<int:user_id>', methods=["GET", "POST"])
def search_movie(user_id):
    # get search_term from url
    title = url_query_parameter(request.url, 'search_term')
    # if search_term was passed, auto_submit = True
    if title:
        auto_submit = True
    else:
        auto_submit = False

    if request.method == "POST":
        user_imdb = data_manager.get_user_imdb_ids(user_id)
        user_imdb_ids = [imdb_id for user_id, imdb_id in user_imdb]
        title = request.form['title']

        try:
            json_resp = search_req(title)
            if "Search" in json_resp:
                movies = json_resp["Search"]
                results = [movie for movie in movies if movie['imdbID'] not in user_imdb_ids]

                return render_template("search-movie.html", user_id=user_id, search_term=title, results=results,
                                       user_imdb_ids=user_imdb_ids, auto_submit=auto_submit)
            else:
                return render_template("notfound.html"), 404
        except ConnectionError as e:
            return render_template("notfound.html"), 404

    return render_template('search-movie.html', user_id=user_id, search_term=title, auto_submit=auto_submit)


@app.route('/users/<int:user_id>/add_movie/<imdb_id>', methods=["POST"])
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
    flash(message)
    return redirect(url_for('search_movie', user_id=user_id, search_term=request.form['title']))


@app.route('/users/<int:user_id>/update_movie/<imdb_id>', methods=["GET", "POST"])
def update_movie(user_id, imdb_id):
    update_form = UpdateMovieForm()
    if request.method == "POST":
        user_movie = data_manager.get_user_movie(user_id, imdb_id)
        user_movie.UserMovie.user_rating = update_form.rating.data
        user_movie.UserMovie.user_review = update_form.review.data
        db.session.commit()

        return redirect(url_for('list_user_movies', user_id=user_id))

    user_movie = data_manager.get_user_movie(user_id, imdb_id)

    update_form.rating.data = user_movie.UserMovie.user_rating
    update_form.review.data = user_movie.UserMovie.user_review
    return render_template('update-movie.html', user_id=user_id,
                           imdb_id=imdb_id, movie=user_movie, form=update_form)


@app.route('/users/<int:user_id>/delete_movie/<imdb_id>', methods=["GET", "POST"])
def delete_movie(user_id, imdb_id):
    if request.method == "POST":
        # Delete User_movie by user_id and imdb_id
        user_movie = data_manager.get_user_movie(user_id, imdb_id)
        data_manager.delete_usermovie(user_movie.UserMovie)
        # check if movie is a favourite of any user
        movie_still_user_favourite = data_manager.check_movie_in_usermovie(imdb_id)
        if not movie_still_user_favourite:
            movie = data_manager.get_movie(imdb_id)
            data_manager.delete_movie(movie)

        return redirect(url_for('list_user_movies', user_id=user_id))

    user_movie = data_manager.get_user_movie(user_id, imdb_id)
    return render_template('delete-movie.html', user_id=user_id, imdb_id=imdb_id, movie=user_movie)


@app.route('/add_user', methods=["GET", "POST"])
def add_user():
    add_form = AddUserForm()
    if request.method == "POST":
        user = User(
            name=add_form.user_name.data
        )
        data_manager.add_user(user)
        return redirect('/users')

    return render_template('add-user.html', form=add_form)


if __name__ == '__main__':
    app.run(debug=True)
