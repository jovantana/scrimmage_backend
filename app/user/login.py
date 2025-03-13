from datetime import datetime
import json
import os

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from app import bcrypt
from app.models import User, db, UserJwtToken
from sqlalchemy import or_

login_bp = Blueprint('login', __name__, url_prefix='/user')
import facebook
from google.oauth2 import id_token
from google.auth.transport import requests


# find existing user
@login_bp.route('/login', methods=['POST'])
def get_user():
    try:
        password = request.json.get('password')
        email = request.json.get('email')
        if not all((email, password)):
            raise ValueError('email or username and password is required')

        user = User.query.filter(or_(User.email == email, User.username == email)).first()
        if not user:
            raise ValueError('email or username does not exists')
        if not bcrypt.check_password_hash(user.password.encode('utf-8'), password):
            raise ValueError('Wrong Credentails')
        token = UserJwtToken.create(user)
        return jsonify({'data': {'token': token.to_json(), 'user_id': user.id}})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# fb login
@login_bp.route('/facebook/auth', methods=['POST'])
def user_facebook_login():
    """
        login with facebook api
    """
    try:
        user_access_token = request.json.get('user_access_token')
        if not user_access_token:
            raise ValueError("user_access_token is required")

        client = facebook.GraphAPI(user_access_token)
        long_live_token = client.extend_access_token(os.getenv('FACEBOOK_APP_ID'), os.getenv('FACEBOOK_APP_SECRET'))
        args = {'fields': 'id,name,email,location', }
        response = client.get_object('me', **args)
        
        print("USER LOCATION: " + str(response.get('location')))
        
        if not response.get('email'):
            raise ValueError('email permission is required')
        user = User.query.filter(User.email == response['email']).first()
        if not user:
            user = User(email=response['email'], username=response['id'], password=None, dob=None,
                        name=response['name'], facebook_user_id=response['id'], created_at=datetime.utcnow())
            if long_live_token.get('access_token'):
                user.facebook_long_live_token = long_live_token['access_token']
            db.session.add(user)
            db.session.commit()
        else:
            user.facebook_user_id = response['id']
            user.updated_at = datetime.utcnow()
            if long_live_token.get('access_token'):
                user.facebook_long_live_token = long_live_token['access_token']
            db.session.commit()
        token = UserJwtToken.create(user)
        return jsonify({'data': {'token': token.to_json(), 'user_id': user.id}})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# google login
@login_bp.route('/google/auth', methods=['POST'])
def user_google_login():
    """
        login/signup with google api
    """
    try:
        google_token = request.json.get('google_token')
        if not google_token:
            raise ValueError('google_token is required')
        response = id_token.verify_oauth2_token(google_token, requests.Request(),
                                                '1066767678808-5kdf9kcpd5389r2g2dp9m86oscgv6tu2.apps.googleusercontent.com')
        if not response.get('email'):
            raise ValueError('email permission is required')
        user = User.query.filter(User.email == response['email']).first()
        if not user:
            user = User(email=response['email'], username=response['sub'], password=None, dob=None,
                        name=response['name'], google_user_id=response['sub'], google_user_token=google_token, created_at=datetime.utcnow())
            db.session.add(user)
            db.session.commit()
        else:
            user.google_user_id = response['sub']
            user.google_user_token = google_token
            user.updated_at = datetime.utcnow()
            db.session.commit()
        token = UserJwtToken.create(user)
        return jsonify({'data': {'token': token.to_json(), 'user_id': user.id}})

    except Exception as e:
        return jsonify({"error": str(e)}), 400
