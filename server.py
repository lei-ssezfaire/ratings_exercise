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
	# print session['current_user']
	flash("Logged Out")

	return render_template('homepage.html')


@app.route('/users')
def user_list():
	"""Show list of users."""

	users = User.query.all()
	return render_template('user_list.html', users=users)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
