from datetime import datetime, timedelta
import jwt
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

import app
from app.authentication.jwt_auth import token_required
from app.models import User, UserJwtToken, Favourite_games

from app.models import db

profile_bp = Blueprint('profile', __name__, url_prefix='/user')


@profile_bp.route('/profile', methods=['GET'])
@token_required
def profile_get(current_user):
    user = User.query.filter_by(id=current_user.id).first()
    return jsonify({'data': user.as_dict()})

@profile_bp.route('/profile', methods=['PATCH'])
@token_required
def profile_update(current_user):
    user = User.query.filter_by(id=current_user.id).first()
    if request.json.get('email', None):
        user.email = request.json.get('email')
    if request.json.get('light_mode', None):
        user.light_mode = request.json.get('light_mode')
    if request.json.get('name', None):
        user.name = request.json.get('name')
    if request.json.get('newsfeed_filters', None):
        user.newsfeed_filters = request.json.get('newsfeed_filters')
    if request.json.get('odds_format', None):
        user.odds_format = request.json.get('odds_format')
    if request.json.get('subscribed_ids', None):
        user.subscribed_ids = request.json.get('subscribed_ids')
    if request.json.get('username', None):
        user.username = request.json.get('username')
    if request.json.get('region', None):
        user.username = request.json.get('region')
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'data': user.as_dict()})


@profile_bp.route('/logout')
@token_required
def logout_user(current_user):
    try:
        token = request.headers['Authorization']

        jwt_obj = UserJwtToken.query.filter_by(jwt_token=token, user_id=current_user.id).first()
        if jwt_obj:
            db.session.delete(jwt_obj)
            db.session.commit()
        else:
            raise ValueError("token is expired or invalid")
        return jsonify({'data': "logout successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@profile_bp.route('/refresh-token')
def jwt_refresh_token():
    try:
        token = request.headers['Authorization']
        refresh_token = request.json.get('refresh_token')
        if not refresh_token:
            raise ValueError("refresh token is required")
        data = jwt.decode(refresh_token, app.config.Config.SECRET_KEY, algorithms=["HS256"])
        jwt_obj = UserJwtToken.query.filter_by(jwt_token=token, refresh_token=refresh_token, user_id=data['user_id']).first()
        if jwt_obj:
            token = jwt_obj.refresh_jwt_token()
            return jsonify({'data': {'token': token.to_json(), 'user_id': token.user_id}})
        else:
            raise ValueError("token is expired or invalid")
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@profile_bp.route('/favourites', methods=['GET'])
@token_required
def favourite_games_get(current_user):
    try:

        fgs = Favourite_games.query.filter(Favourite_games.user_id==current_user.id).all()
        
        fgs_json = [fg.as_dict() for fg in fgs]    
    
        return jsonify(fgs_json), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@profile_bp.route('/favourites', methods=['POST'])
@token_required
def favourite_games_add(current_user):
    try:
        game_id = request.json.get('game_id')
        game_date = request.json.get('game_date')
        
        fg = Favourite_games(user_id=current_user.id, game_id=game_id, game_date=game_date)
        db.session.add(fg)
        db.session.commit()
    
        return {"message": "done"}, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@profile_bp.route('/favourites', methods=['DELETE'])
@token_required
def favourite_games_delete(current_user):
    try:
        id = request.json.get('id')
        
        fg = Favourite_games.query.filter(Favourite_games.user_id==current_user.id, Favourite_games.id==id).first()

        db.session.delete(fg)
        db.session.commit()
    
        return {"message": "done"}, 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def delete_old_favourite_games(app, db):
    """ Function to delete favourite games older than 2 days
        from Postgres database
    """
    with app.app_context():
        try:
            now = int(datetime.now().replace(microsecond=0).timestamp())
            today = datetime.fromtimestamp(now)
            expiration = today - timedelta(days=2)

            Favourite_games.query.filter(Favourite_games.game_date <= expiration).delete()
            db.session.commit()

            print("Favourite games deleted successfully!")
        except Exception as e:
            print(f"Error deleting favourite games: {e}")