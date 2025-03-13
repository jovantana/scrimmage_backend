from flask import Blueprint, request
from app.config import REGIONS, rd
import ast
import pandas as pd
from datetime import datetime

odds_bp = Blueprint('odds', __name__, url_prefix='/odds')


@odds_bp.route('/get', methods=['GET'])
def get_odds():
    """Endpoint to list odds from Redis"""

    data = rd.get('odds')

    if data:
        data_str = data.decode("utf-8")
        data_json = ast.literal_eval(data_str)
        response = {'data': data_json}
        status = 200
    else:
        response = {'data': "no data"}
        status = 203

    return response, status


@odds_bp.route('/getgames', methods=['GET'])
def get_games():
    """ Endpoint to get games filtering by:
        league, league_code, date_and_time and game_id
    """
    
    league = request.args.get('league', '*')
    league_code = request.args.get('league_code', '*')
    date_and_time = request.args.get('date_and_time', '*')
    game_id = request.args.get('game_id', '*')
    region = request.args.get('region', False)

    # Filter by range of dates
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    # Check if it'll filter by range of dates then get all odds first
    key = "odds:" + ":".join([league, league_code, date_and_time, game_id])

    games_list = []
    keys = rd.keys(pattern=key)

    for key in keys:        
        game = rd.get(key)
        game_str = game.decode("utf-8")
        game_json = ast.literal_eval(game_str)
        
        # Filter by region
        if region:
            odds = game_json['odds']
            
            new_odds = []

            for bet_type in odds:
                bet_name = list(bet_type.keys())[0]
                
                selected_books = []
                
                for book in bet_type[bet_name]:
                    book_name = book['book']
                    
                    book_sufix = book_name.split("_")[-1]
                    if book_sufix in REGIONS:
                        if book_sufix == region:
                            selected_books.append(book)
                    else:
                        selected_books.append(book)
                
                bet_type = { f"{bet_name}": selected_books }
                new_odds.append(bet_type)

            game_json['odds'] = new_odds

        games_list.append(game_json)

    if games_list:
        # Check if it's filtering by range of dates
        if start_date:
            # Convert list of games to dataframe
            games_df = pd.DataFrame(games_list)

            # Convert dates to datetime for filtering
            games_df['date_and_time'] = pd.to_datetime(games_df['date_and_time'],unit='s')
            start_date = datetime.fromtimestamp(int(start_date))
            end_date = datetime.fromtimestamp(int(end_date))

            # Filter by range of dates
            games_df = games_df[
                (games_df['date_and_time'] >= start_date) & \
                (games_df['date_and_time'] <= end_date)
            ]

            # Convert back to unix time
            games_df['date_and_time'] = games_df.date_and_time.astype('int64') // 10**9

            # Convert dataframe to list of dicts
            games_list = games_df.to_dict('records')

        response = {'data': games_list}
        status = 200
    else:
        response = {'data': "no data"}
        status = 203
    
    return response, status
