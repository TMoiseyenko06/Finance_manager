import os
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

def encode_token(user_id):
    payload = {
        'exp' : datetime.now() + timedelta(days=1),
        'iat' : datetime.now(),
        'usr' : user_id
    }
    token = jwt.encode(payload,SECRET_KEY,algorithm='HS256')
    return token

def verify_token():
    token = None
    if 'Authorization' in request.headers:
        try:
            token = request.headers['Authorization'].split(" ")[1]
            jwt.decode(token,SECRET_KEY,algorithms='HS256')
        except jwt.ExpiredSignatureError:
            return jsonify({
                "status":"BAD",
                "message":"Token has Expired"
            }),401
        except jwt.InvalidTokenError:
            return jsonify({
                "status":"BAD",
                "message":"Invalid Token"
            }),401
    if not token:
        return jsonify({
            "status":"BAD",
            "message":"Token is Missing"
        }),401
    return jsonify({
            "status":"BAD",
            "message":"Token is Missing"
        }),401

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        error_response = verify_token()
        if error_response:
            return error_response
        return f(*args,**kwargs)
    return decorated
