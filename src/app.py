from flask import Flask

# import database and classes
from models import db
from models import User

# import server config
from config import Config

from random import sample
from string import ascii_letters, digits
from werkzeug.security import generate_password_hash

# import blueprints
from ui import ui
from api import api

app = Flask(__name__)
app.config.from_object(Config())
app.register_blueprint(ui)
app.register_blueprint(api)
db.init_app(app)


@app.cli.command()
def initdb():
	db.drop_all()
	db.create_all()
	# create random password
	passwd = ''.join(sample(ascii_letters+digits, 50))
	with open ("password.txt", "w") as f:
		f.write(f"Your password is [ {passwd} ]")
	f.close()
	# create user with generated password
	usr = User(username="admin", passhash=generate_password_hash(passwd, "sha256"))
	db.session.add(usr)
	db.session.commit()
