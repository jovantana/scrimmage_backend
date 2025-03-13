import ast
import json
import requests
from datetime import datetime, timedelta
import time
from app.config import REGIONS, rd
from flask import request

from flask import Blueprint
from app.config import META_KEY

side_odds_bp = Blueprint('side_odds', __name__, url_prefix='/side_odds')

@side_odds_bp.route('futures')
def get_futures():
    start_time = time.time()
    
    game_code = request.args.get('game_code', '*')
    league_code = request.args.get('league_code', '*')
    bet_type = request.args.get('bet_type', '*')
    game_id = request.args.get('game_id', '*')
    team_id = request.args.get('team_id', '*')
    player_id = request.args.get('player_id', '*')
    region = request.args.get('region', False)
    
    key = "futures:"+ ":".join([game_code, league_code, bet_type, game_id, team_id, player_id])
    print("Fetching futures for " + key)
    
    futures = {}
    keys = rd.keys(pattern=key)
    for key in keys:
        side_odd = rd.get(key)
        side_odd_str = side_odd.decode("utf-8")
        side_odd_json = ast.literal_eval(side_odd_str)
        
        blocks = str(key)[2:].split(":")
        
        filtered_by_region = filter_by_region(side_odd_json, region)
        generate_key_structure(futures, blocks, filtered_by_region)
        
    end_time = time.time()
    print("get_futures execution time: " + str(end_time - start_time))
    
    return str(futures)

@side_odds_bp.route('side_odds')
def get_side_odds():
    start_time = time.time()
    
    game_code = request.args.get('game_code', '*')
    league_code = request.args.get('league_code', '*')
    bet_type = request.args.get('bet_type', '*')
    game_id = request.args.get('game_id', '*')
    team_id = request.args.get('team_id', '*')
    player_id = request.args.get('player_id', '*')
    region = request.args.get('region', False)
    
    key = "side_odds:"+ ":".join([game_code, league_code, bet_type, game_id, team_id, player_id])
    print("Fetching side_odds for " + key)
    
    side_odds = {}
    keys = rd.keys(pattern=key)
    for key in keys:
        side_odd = rd.get(key)
        side_odd_str = side_odd.decode("utf-8")
        side_odd_json = ast.literal_eval(side_odd_str)
        
        blocks = str(key)[2:].replace("'", "").split(":")

        filtered_by_region = filter_by_region(side_odd_json, region)
        generate_key_structure(side_odds, blocks, filtered_by_region)
        
    end_time = time.time()
    print("get_side_odds execution time: " + str(end_time - start_time))
    
    return json.dumps(side_odds)
    
def generate_key_structure(dict, blocks, value):
    last_layer = dict
    for block in blocks[:-1]:
        if block not in last_layer:
            last_layer[block] = {}
        last_layer = last_layer[block]
        
    last_layer[blocks[-1]] = value
    
def filter_by_region(odds, region):
    bet_for = odds['bet_for']
    bet_against = odds['bet_against']
    
    filtered_bet_for = []
    filtered_bet_against = []
    
    for book in bet_for:
        book_name = book['provider']
        
        book_sufix = book_name.split("_")[-1]
        if book_sufix in REGIONS:
            if book_sufix == region:
                filtered_bet_for.append(book)
        else:
            filtered_bet_for.append(book)
            
    for book in bet_against:
        book_name = book['provider']
    
        book_sufix = book_name.split("_")[-1]
        if book_sufix in REGIONS:
            if book_sufix == region:
                filtered_bet_against.append(book)
        else:
            filtered_bet_against.append(book)
            
    return {'bet_for': filtered_bet_for, 'bet_against': filtered_bet_against}
    