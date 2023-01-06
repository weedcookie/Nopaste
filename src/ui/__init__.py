from flask import render_template
from flask import make_response
from flask import Blueprint
from flask import redirect
from flask import session
from flask import request
from flask import flash
from flask import abort 

from uuid import uuid4
from secrets import token_hex

# import database and classes
from models import db
from models import User
from models import Paste

# used for decorator functions
from functools import wraps

# used to validate and create user password hash 
from werkzeug.security import generate_password_hash, check_password_hash


# user validator 
def check_user(f):
	@wraps(f)
	def check(*args, **kwargs):
		if session.get('user'):
			return f(*args, **kwargs)
		else:
			session.clear()
			return redirect('/login')
	return check

ui = Blueprint("ui", __name__, template_folder="templates")

@ui.route('/', methods=["GET","POST"])
def index():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		if not username or not password:
			flash("Please fill all fields", "error")
		# check if user is already in the database else create the new user 
		usr = User.query.filter_by(username=username).first()
		if usr:
			flash(f"Username {username} is already taken.", "error")
		else:
			usr = User(username=username, passhash=generate_password_hash(password , "sha256"))
			db.session.add(usr)
			db.session.commit()
			flash(f"Added {usr.username} to the database.", "success")
			return redirect("/")
		return render_template("signup.html")
	else:
		return render_template("signup.html")


@ui.route('/login', methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form.get('username')
		password = request.form.get('password')

		if not username or not password:
			flash("Please fill in all fields.","error")

		# grab user with this username from the database 
		usr = User.query.filter_by(username=username).first()
		if not usr:
			flash(f"User {username} not in the database.","error")
			return render_template("login.html")

		# check provided password 
		if check_password_hash(usr.passhash, password):
			session['user'] = usr.username
			return redirect("/home")
		else:
			flash("Wrong credentials provided", "error")
		return render_template("login.html")
	else:
		return render_template("login.html")


@ui.route("/home")
@check_user
def home():
	usr = User.query.filter_by(username=session['user']).first()
	if not usr:
		return redirect("/login")
	pastes = Paste.query.filter_by(user_id=usr.id)
	return render_template("home.html", pastes=pastes)


@ui.route("/profile")
def profile():
	# used to change user password and create api keys
	usr = User.query.filter_by(username=session.get('user')).first()
	if not usr:
		flash("An error has happend.")
		return redirect("/home")
	private_pastes = Paste.query.filter_by(user_id=usr.id, private=True).count()
	public_pastes = Paste.query.filter_by(user_id=usr.id, private=False).count()

	return render_template("profile.html", usr=usr, private_pastes=private_pastes, public_pastes=public_pastes)




@ui.route("/paste", methods=["GET","POST"])
@check_user
def paste():
	usr = User.query.filter_by(username=session['user']).first()
	if request.method == "POST":
		raw_text = request.form.get('raw_text')
		private = request.form.get('private_paste')
		
		if private and private.upper() == "ON":
			paste = Paste(text=raw_text, user_id=usr.id, private=True, paste_id=str(uuid4()))
		else:
			paste = Paste(text=raw_text, user_id=usr.id, paste_id=str(uuid4()))

		db.session.add(paste)
		db.session.commit()
		flash("Add new paste", "source")
		return render_template("paste.html")
	else:
		return render_template("paste.html")


@ui.route("/raw/<paste_id>")
def raw_paste(paste_id):
	paste = Paste.query.filter_by(paste_id=paste_id).first()
	if not paste:
		return redirect("/_")
	resp = make_response(paste.text)
	resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
	return resp




@ui.route("/change_username", methods=["POST"])
def change_username():
	usr = User.query.filter_by(username=session.get('user')).first()
	if not usr:
		abort()
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password1")

		# check if username is already taken 
		check = User.query.filter_by(username=username).first()
		if check:
			flash(f"{username} is already taken", "error")
			return redirect("/profile")

		# check password 
		if check_password_hash(usr.passhash, password):
			usr.username = username
			db.session.commit()
			flash(f"Updated username to {username}", "success")
			return redirect("/logout")
	return redirect('/profile')



@ui.route("/change_password", methods=["POST"])
def change_password():
	usr = User.query.filter_by(username=session.get('user')).first()
	if not usr:
		return redirect("/profile")

	if request.method == "POST":
		old = request.form.get("password2")
		new = request.form.get("password3")

		# check password
		if check_password_hash(usr.passhash, old):
			usr.passhash = generate_password_hash(new, "sha256")
			db.session.commit()
			flash("Updated password.", "success")
		else:
			flash("Wrong password provided", "error")
			return redirect("/profile")
	return redirect('/profile')



@ui.route("/change_api", methods=["POST"])
def change_api():
	usr = User.query.filter_by(username=session.get("user")).first()
	if not usr:
		flash("an error has happend", "error")
		return redirect("/profile")

	if request.method == "POST":
		api_key = request.form.get("api_key")
		usr.api_key = api_key
		db.session.commit()
		flash("Updated API key", "success")
	return redirect('/profile')


@ui.route('/logout')
def logout():
	session.clear()
	return redirect("/login")


@ui.app_errorhandler(404)
def not_found(e):
	return render_template("error.html")