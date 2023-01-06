from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique=True, nullable=False)
	passhash = db.Column(db.String, nullable=False)
	api_key = db.Column(db.String, nullable=True, unique=True)

class Paste(db.Model):
	__tablename__ = "pastes"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, default="Untitled")
	text = db.Column(db.Text)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	private = db.Column(db.Boolean, default=False)
	paste_id = db.Column(db.String, nullable=False)
	datetime = db.Column(db.String, nullable=False, default=datetime.utcnow())
