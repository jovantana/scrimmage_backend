from functools import wraps

from flask import jsonify, request
from pytz import unicode

import app
import jwt
import datetime
from app.models import User, UserJwtToken


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return jsonify({'error': 'a valid token is missing'})
        try:
            current_user = validate_jwt_token(token)
        except Exception:
            return jsonify({'error': 'token is invalid'}), 401
        return f(current_user, *args, **kwargs)

    return decorator


def create_jwt_token(user, expire_time):
    token = jwt.encode({'user_id': user.id, 'exp': expire_time},
                       app.config.Config.SECRET_KEY, algorithm="HS256")
    return unicode(token)

def validate_jwt_token(token):
    token_obj = UserJwtToken.query.filter_by(jwt_token=token).first()
    if not token_obj:
        raise ValueError('token is invalid')
    data = jwt.decode(token, app.config.Config.SECRET_KEY, algorithms=["HS256"])
    current_user = User.query.filter_by(id=data['user_id']).first()
    
    return current_user