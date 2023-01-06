from flask import render_template
from flask import make_response
from flask import current_app
from flask import Blueprint
from flask import redirect
from flask import request
from flask import session
from flask import jsonify
from flask import flash
from flask import abort 

# import database and classes
from models import db
from models import User
from models import Paste

# used for decorator functions
from functools import wraps

def check_api_key(f):
	@wraps(f)
	def check(*args, **kwargs):
		# check if api key is provided 
		# check if key and json data are related to the same user
		if request.headers.get("API-KEY"):
			api_key = request.headers.get("API-KEY")

			# check if 
			usr = User.query.filter_by(api_key=api_key).first()
			if not usr:
				return jsonify({"Status":"Error","Msg":"wrong API key."}),200	


			# if not request.json:
			# 	return jsonify({"Status":"Error","Msg":"No json data found"}),200

			# # check if paste id is provided
			# if request.json:
			# 	json_data = request.json
			# 	if json_data.get('paste_id'):
			# 		paste = Paste.query.filter_by(user_id=usr.id).first()
			# 		# check if paste.user_id == usr.id 
			# 		if paste.user_id == usr.id:
			# 			return f(*args, **kwargs)
			# 		else:
			# 			return jsonify({"Status":"Error","Msg":"No paste with such API ket"}),200
			# 	else:
			# 		return jsonify({"Status":"Error","Msg":"No paste id found"}),200
			# else:
			# 	return jsonify({"Status":"Error","Msg":"No json data found"}),200
			return f(*args, **kwargs)
		else:
			# API key not found
			return jsonify({"Status":"Error","Msg":"No API found"}),200


		return jsonify({"Status":"Error","Msg":"An Error has occurred."}),200

	return check



api = Blueprint("api", __name__ , url_prefix="/api")

@api.route('/edit', methods=["POST"])
@check_api_key
def edit_paste():
	'''
		{
			"paste_id":"a8ca8103-ddfe-4845-bbea-8c758395a36a",
			"text":"hello world"
		}
	'''
	if request.method == "POST":
		# check for json data 
		if not request.json:
			return jsonify({"Status":"Error","Msg":"No json data found"}),200	

		json_data = request.json

		paste = Paste.query.filter_by(paste_id=json_data.get('paste_id')).first()
		if not paste:
			return jsonify({"Status":"Error","Msg":"Wrong paste id"}),200

		
		if not json_data.get('paste_id') or not json_data.get('text'):
			return jsonify({"Status":"Error","Msg":"Missing json values"}),200

		# update text 
		paste.text = json_data.get('text')
		db.session.commit()
		return jsonify({"Status":"Success","Msg":"Updated paste text"}),200
	else:
		return jsonify({"Status":"Error","Msg":"Wrong request method"}),200


@api.route('/get', methods=["GET"])
@check_api_key
def get_paste():
	'''
		returns a single paste in the form of json response
		json request 
		{
			"paste_id":"a8ca8103-ddfe-4845-bbea-8c758395a36a"
		}
		json response 
		{
		    "Msg": "Paste found",
		    "Status": "Success",
		    "text": "hello world"
		}
	'''
	if request.method == "GET":
		# check for json data 
		if not request.json:
			return jsonify({"Status":"Error","Msg":"No json data found"}),200	

		json_data = request.json

		if not json_data.get("paste_id"):
			return jsonify({"Status":"Error","Msg":"Missing json values"}),200

		paste = Paste.query.filter_by(paste_id=json_data.get('paste_id')).first()
		if not paste:
			return jsonify({"Status":"Error","Msg":"Wrong paste id"}),200

		return jsonify({"Status":"Success","Msg":"Paste found","text":f"{paste.text}"}),200

	else:
		return jsonify({"Status":"Error","Msg":"Wrong request method"}),200



@api.route("/all", methods=["GET"])
@check_api_key
def all_pastes():
	'''
		returns all pastes provided by user with current api key 
	'''
	data = {}
	if request.method == "GET":
		if not request.headers.get("API-KEY"):
			return jsonify({"Status":"Error","Msg":"No API key."}),200
		usr = User.query.filter_by(api_key=request.headers.get("API-KEY")).first()
		pastes = Paste.query.filter_by(user_id=usr.id).all()
		if not pastes:
			return jsonify({"Status":"Success","Msg":"No pastes found"}),200

		for paste in pastes:
			data[paste.paste_id] = {"name":paste.name,
						   "text":paste.text,
						   "private":paste.private,
						   "modified":paste.datetime}
		return jsonify({"Status":"Success","Msg":f"found {len(pastes)} pastes", "Data":data}),200

	else:
		return jsonify({"Status":"Error","Msg":"Wrong request method"}),200


@api.route("/private")
@check_api_key
def private():
	data = {}
	if request.method == "GET":
		if not request.headers.get("API-KEY"):
			return jsonify({"Status":"Error","Msg":"No API key."}),200
		usr = User.query.filter_by(api_key=request.headers.get("API-KEY")).first()
		pastes = Paste.query.filter_by(user_id=usr.id, private=True).all()
		if not pastes:
			return jsonify({"Status":"Success","Msg":"No pastes found"}),200

		for paste in pastes:
			data[paste.paste_id] = {"name":paste.name,
						   "text":paste.text,
						   "modified":paste.datetime}
		return jsonify({"Status":"Success","Msg":f"found {len(pastes)} pastes", "Data":data}),200

	else:
		return jsonify({"Status":"Error","Msg":"Wrong request method"}),200


@api.route("/public")
@check_api_key
def public():
	data = {}
	if request.method == "GET":
		if not request.headers.get("API-KEY"):
			return jsonify({"Status":"Error","Msg":"No API key."}),200
		usr = User.query.filter_by(api_key=request.headers.get("API-KEY")).first()
		pastes = Paste.query.filter_by(user_id=usr.id, private=False).all()
		if not pastes:
			return jsonify({"Status":"Success","Msg":"No pastes found"}),200

		for paste in pastes:
			data[paste.paste_id] = {"name":paste.name,
						   "text":paste.text,
						   "private":paste.private,
						   "modified":paste.datetime}
		return jsonify({"Status":"Success","Msg":f"found {len(pastes)} pastes", "Data":data}),200

	else:
		return jsonify({"Status":"Error","Msg":"Wrong request method"}),200


@api.route("/delete", methods=["GET"])
@check_api_key
def delete_pastes():
	if request.method == "GET":
		if not request.headers.get("API-KEY"):
			return jsonify({"Status":"Error","Msg":"No API key."}),200
		
		if not request.json:
			return jsonify({"Status":"Error", "Msg":"No json found"}), 200

		usr = User.query.filter_by(api_key=request.headers.get("API-KEY")).first()
		if not usr:
			return jsonify({"Status":"Error","Msg":"No user with such API key"}),200

		paste_id = request.json.get("paste_id")
		if not paste_id:
			return jsonify({"Status":"Error", "Msg":"No paste ID found"})


		paste = Paste.query.filter_by(user_id=usr.id, paste_id=paste_id).first()

		if not paste:
			return jsonify({"Status":"Error", "Msg":"No such paste for provided key or paste ID"}), 200

		deleted_paste_id = paste.paste_id
		db.session.delete(paste)
		db.session.commit()
		return jsonify({"Status":"Success", "Msg":f"Delete paste with id {deleted_paste_id}"})
	else:
		return jsonify({"Status":"Error","Msg":"Wrong request method"}),200


@api.app_errorhandler(400)
def bad_syntax(e):
	current_app.logger.error(e)
	return jsonify({"Status":"Error","Msg":"Malformed request, this will be reported"}),200

@api.app_errorhandler(404)
def not_found(e):
	return jsonify({"Status":"Error","Msg":"Endpoint not found"}),200

@api.app_errorhandler(405)
def wrong_request(e):
	return jsonify({"Status":"Error","Msg":"Wrong request found"}),200

@api.app_errorhandler(401)
def unauthorized(e):
	return jsonify({"Status":"Error","Msg":"Not authorized"}),200

@api.app_errorhandler(500)
def server_error(e):
	current_app.logger.error(e)
	return jsonify({"Status":"Error","Msg":"Server error, this will be reported"}),200