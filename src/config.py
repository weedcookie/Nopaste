from random import sample 
from string import ascii_letters, digits


class Config:
	SECRET_KEY = ''.join(sample(ascii_letters+digits, 40))
	SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	
