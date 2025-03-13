import ast
from app.authentication.jwt_auth import validate_jwt_token
import json
from flask import Blueprint, make_response, jsonify
from flask_cors import cross_origin
from app.config import REGIONS, socketio
from flask_socketio import join_room
from app.config import TEAM_LOGOS
import requests
from flask import request, redirect
from app.models import Affiliates, OddsTypeEnum
from app.config import rd

home_bp = Blueprint('home', __name__, url_prefix='/')


@home_bp.route('')
def home():
    return 'main home route'

@home_bp.route('/images/teams/<pid>.png')
def get_image(pid):
    logos_filtered = list(filter(lambda logo: pid in logo, TEAM_LOGOS['data']))

    if len(logos_filtered) > 0 and logos_filtered[0][pid] != "None":
        logo_url = logos_filtered[0][pid]
        img_data = requests.get(logo_url, allow_redirects=True).content
    
        response = make_response(img_data)
        response.headers.set('Content-Type', 'image/jpeg')
        return response
    else:
        return ('', 204)
    
@home_bp.route('/regions')
def get_regions():
    return jsonify(REGIONS)

@home_bp.route('/affiliate')
def get_affiliate_link():
    game_id = request.args.get('game_id')
    bet_type = request.args.get('bet_type')
    odd_type = request.args.get('odd_type')
    book = request.args.get('book')
    bet_for = json.loads(request.args.get('bet_for', 'true').lower())
    
    affiliate = Affiliates.query.filter(Affiliates.book == book).first()
    
    try:
    
        if affiliate and affiliate.link:
            return redirect(affiliate.link, code=302)
        elif odd_type == OddsTypeEnum.odds.value:
            key_pattern = "odds:*" + str(game_id)
            
            keys = rd.keys(pattern=key_pattern)

            game = rd.get(keys[0])
            game_str = game.decode("utf-8")
            game_json = ast.literal_eval(game_str)
            
            odds = game_json['odds']
            
            odds_for_bet_type = list(filter(lambda odd: bet_type in odd.keys(), odds))
            
            odd_for_book = list(filter(lambda odd: odd['book'] == book, odds_for_bet_type[0][bet_type]))
            
            return redirect(odd_for_book[0]['book_url'], code=302)
        else:
            key_pattern = odd_type + "*" + bet_type + "*" +  str(game_id) + "*"
            
            keys = rd.keys(pattern=key_pattern)

            game = rd.get(keys[0])
            game_str = game.decode("utf-8")
            game_json = ast.literal_eval(game_str)
            
            odds = []
            if bet_for:
                odds = game_json['bet_for']
            else:
                odds = game_json['bet_against']
                
            odd_for_book = list(filter(lambda odd: odd['provider'] == book, odds))
            
            return redirect(odd_for_book[0]['url'], code=302)
    except Exception as err:
        return jsonify({"error": str(err)}), 400

@socketio.on('join')
def on_join(data):
    room_id = data.get('id', None)
    if not room_id:
        socketio.emit("error", "No room id", to=request.sid)
    join_room(room_id)
    print("Someone has joined room: " + room_id)
    
@socketio.on('join_user_room')
def on_join(data):

    room_id = data.get('id', 0)
    token = data.get('Authorization', None)
    try:
        validate_jwt_token(token)
    except Exception as err:
        socketio.emit("error", str(err), to=request.sid)
    else:
        join_room(room_id)
        print("Someone has joined room: " + room_id)

@socketio.on_error_default
def error_handler(e):
    print('An error has occurred in sockets: ' + str(e))

#odds must go here