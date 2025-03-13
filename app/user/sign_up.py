from datetime import datetime
import json
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from app import bcrypt
from app.models import User, db

signup_bp = Blueprint('sign_up', __name__, url_prefix='/user')

#Auth0 check + add user to db, change into post req
@signup_bp.route('/sign_up', methods=['POST'])
def sign_up():
    try:
        if not request.json:
            raise ValueError('password, email, username, dob are required fields')
        password = request.json.get('password')
        confirm_password = request.json.get('confirm_password')
        email = request.json.get('email')
        username = request.json.get('username')
        name = request.json.get('name')
        dob = request.json.get('dob')
        region = request.json.get('region')
        if not dob:
            ValueError("dob is required")

        if not password:
            ValueError("password is required")

        if User.query.filter_by(email=email).first():
            raise ValueError('email already exists')
        
        if User.query.filter_by(username=username).first():
            raise ValueError('username already exists')

        if password != confirm_password:
            raise ValueError('password and confirm password is not same')
        

        crypt_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email=email, username=username, password=crypt_password, dob=dob, name=name, created_at=datetime.utcnow(), region=region)
        db.session.add(user)
        db.session.commit()
        return jsonify({"data": user.as_dict(), "message": "user registered"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
