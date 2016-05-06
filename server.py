"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db



app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')


@app.route('/show-sign-in')
def signin():
    """Show sign-in page"""

    return render_template('sign_in.html')

@app.route('/handle-sign-in')
def handle_signin():
	"""Get username, check against database and add if it doesn't exist"""

	email = request.args.get("email")
	password = request.args.get("password")

	# check the db to see if username exists
	all_users = User.query.filter(User.email == email).all()

	if not all_users:
		db.session.add(User(email=email, password=password))
		db.session.commit()

	session['current_user'] = email

	flash("Logged in.")
	return render_template('homepage.html')


@app.route('/handle-log-out')
def handle_log_out():

	session['current_user'] = None
	flash("Logged Out")

	return render_template('homepage.html')

@app.route('/users/<int:user_id>')
def user_info(user_id):


	user = User.query.filter_by(user_id=user_id).one()
	email = user.email
	age = user.age
	zipcode = user.zipcode
	rating_list = Rating.query.filter_by(user_id=user_id).all()
	list_of_movie_ratings =[]

	for rating in rating_list:
		movie_id = rating.movie_id
		score = rating.score
		movie_info = Movie.query.filter_by(movie_id=movie_id).one()
		movie_title = movie_info.title
		the_tuple = (movie_title, score)
		list_of_movie_ratings.append(the_tuple)

	return render_template('user_info.html', email=email, age=age, zipcode=zipcode, title_score_tuple_list=list_of_movie_ratings)


@app.route('/handle_rating')
def handle_rating():
	"""Handles movie ratings"""

	rating = request.args.get('user_score')

	movie_info = request.args.get('movie_info')
	print '*' * 50
	print movie_info
	print type(movie_info)
	print '*' * 50
	movie_list = [x.encode('UTF8') for x in movie_info]
	movie_title = str(movie_list[0])

	print "HERE IT IS!"
	print movie_title
	print '*' * 50

	user = session['current_user']

	#use movie_title to get movie_id
	movie_id = db.session.query(Movie.movie_id).filter_by(title=movie_title).one()
	# see the combination of movie_id, and our user is in a Rating row
	rating_row = db.session.query(rating_id).filter_by(movie_id=movie_id, user_id=user).one()
	if rating_row:
		rating_row.score = rating
		db.session.commit()
	else:
		new_row = Rating(movie_id=movie_id, user_id=user, score=rating)
		db.session.add(new_row)
		db.session.commit()

	# if it is, update that rating row with new value
	# if not insert new rating
	movies = db.session.query(Movie.title, Rating.user_id, Rating.score).join(Rating)
	specific_movie = movies.filter_by(movie_id = movie_id).all()


	return render_template('movie_info.html', movie_title= movie_title, specific_movie=specific_movie)


@app.route('/movies/<int:movie_id>')
def movie_info(movie_id):
	
	movies = db.session.query(Movie.title, Rating.user_id, Rating.score).join(Rating)
	specific_movie = movies.filter_by(movie_id = movie_id).all()
	movie_title = specific_movie[0][0]

	return render_template('movie_info.html', movie_title=movie_title, specific_movie=specific_movie)

@app.route('/users')
def user_list():
	"""Show list of users."""

	users = User.query.all()
	return render_template('user_list.html', users=users)



@app.route('/movies')
def movie_list():
	"""Show list of movies."""

	movies = Movie.query.order_by('title').all()
	return render_template('movie_list.html', movies=movies)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
