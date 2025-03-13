from app.models import OddsTypeEnum, UserBet
import os
import requests
import json
from app.config import META_KEY, rd, socketio
import ast
import time
from datetime import datetime
import dateutil.relativedelta


def update_odds(app, db):
    """Endpoint to update odds on Redis"""
    print("UPDATING ODDS")

    leagues = [
        'ncaabaseball',
        'ncaaf',
        'ncaab',
        'golf',
        'mlb',
        'mma',
        'nfl',
        'nhl',
        'soccer',
        'tennis', 
        'wnba',
        'ncaabw',
        'esports'
    ]

    all_league_data = []

    for league in leagues:

        json_data = open(os.path.join(
            'app/betting/json_scripts', 'league_codes.json'), 'r')
        teams_data = json.load(json_data).get('data')

        *misc, = []
        for teams in teams_data:
            *abv, = teams
            misc.append(abv)

        parameters = {
            'sport': league,
            'apiKey': META_KEY
        }

        req = requests.get(
            f'https://scrimmage.api.areyouwatchingthis.com/api/odds.json?',
            params=parameters)
        
        # checks to see if there are results at all

        results = req.json().get('results')
        if results == []:
            continue

        data = []
        if len(results) > 1:

            for game_data in results:

                """INITIATES ARRAYS FOR EACH BET TYPE"""
                spreadTeam1array = []
                spreadTeam2array = []
                overarray = []
                underarray = []
                moneylineTeam1array = []
                moneylineTeam2array = []

                game_id = game_data.get('gameID')
                date_and_time = game_data.get('date')
                # removes the miliseconds from the time. Gets to seconds
                if date_and_time:
                    date_and_time = round(date_and_time/1000, None)
                odds = game_data.get('odds')
                for sportbook in odds:

                    """RETRIEVES DATA"""
                    book = (sportbook.get('provider'))
                    spreadLine1 = sportbook.get('spreadLine1')
                    spreadTeam1 = sportbook.get('spread')
                    spreadLine2 = sportbook.get('spreadLine2')
                    book_url = sportbook.get('url')
                    try:
                        spreadTeam2 = float(spreadTeam1)*-1
                    except TypeError:
                        spreadTeam2 = None
                    overLine = sportbook.get('overUnderLineOver')
                    underLine = sportbook.get('overUnderLineUnder')
                    OverUnderHandicap = sportbook.get('overUnder')
                    moneylineTeam1 = sportbook.get('moneyLine1')
                    moneylineTeam2 = sportbook.get('moneyLine2')

                    # converts decimal price to american price and stores both
                    def decimal_to_american(decimal_price):
                        if decimal_price > 2:
                            american_price = round(
                                (decimal_price - 1) * 100, None)
                        else:
                            american_price = round(-100 /
                                                   (decimal_price - 1), None)
                        return american_price

                    """ CHECKS IF THERE IS SPREAD DATA 
                        AND APPENDS TO EACH BET TYPE ARRAY """
                    if (spreadLine1 == None or 
                        spreadTeam1 == None or 
                        book == 'CONSENSUS'):
                        pass
                    else:
                        american_price = decimal_to_american(spreadLine1)
                        spreadTeam1array.append(
                            {
                                'handicap': spreadTeam1, 
                                'american_price': american_price, 
                                'decimal_price': spreadLine1, 
                                'book': book,
                                'book_url': book_url
                            }
                        )
                        american_price = decimal_to_american(spreadLine1)

                    if (spreadLine2 == None or 
                        spreadTeam2 == None or 
                        book == 'CONSENSUS'):
                        pass
                    else:
                        american_price = decimal_to_american(spreadLine2)
                        spreadTeam2array.append(
                            {
                                'handicap': spreadTeam2,
                                'american_price': american_price,
                                'decimal_price': spreadLine2,
                                'book': book,
                                'book_url': book_url
                            }
                        )

                    """ CHECKS IF THERE IS OVER/UNDER DATA 
                        AND APPENDS TO EACH BET TYPE ARRAY """
                    if (overLine == None or 
                        OverUnderHandicap == None or 
                        book == 'CONSENSUS'):
                        pass
                    else:
                        american_price = decimal_to_american(overLine)
                        overarray.append(
                            {
                                'handicap': OverUnderHandicap, 
                                'american_price': american_price, 
                                'decimal_price': overLine, 
                                'book': book,
                                'book_url': book_url
                            }
                        )

                    if (underLine == None or 
                        OverUnderHandicap == None or 
                        book == 'CONSENSUS'):
                        pass
                    else:
                        american_price = decimal_to_american(underLine)
                        underarray.append(
                            {
                                'handicap': OverUnderHandicap,
                                'american_price': american_price,
                                'decimal_price': underLine,
                                'book': book,
                                'book_url': book_url
                            }
                        )

                    """ CHECKS IF THERE IS MONEYLINE DATA 
                        AND APPENDS TO EACH BET TYPE ARRAY """
                    if moneylineTeam1 == None or book == 'CONSENSUS':
                        pass
                    else:
                        american_price = decimal_to_american(moneylineTeam1)
                        moneylineTeam1array.append(
                            {
                                'american_price': american_price,
                                'decimal_price': moneylineTeam1,
                                'book': book,
                                'book_url': book_url
                            }
                        )

                    if (moneylineTeam2 == None or 
                        moneylineTeam2 == 'None' or 
                        book == 'CONSENSUS'):
                        pass
                    else:
                        american_price = decimal_to_american(moneylineTeam2)
                        moneylineTeam2array.append(
                            {
                                'american_price': american_price,
                                'decimal_price': moneylineTeam2,
                                'book': book,
                                'book_url': book_url
                            }
                        )

                """SORTS EACH BET TYPE ARRAY BY HIGHEST LINE VALUE FIRST"""
                spreadTeam1array.sort(
                    key=lambda x: x['decimal_price'], reverse=True)

                spreadTeam2array.sort(
                    key=lambda x: x['decimal_price'], reverse=True)

                overarray.sort(key=lambda x: x['decimal_price'], reverse=True)
                underarray.sort(key=lambda x: x['decimal_price'], reverse=True)

                moneylineTeam1array.sort(
                    key=lambda x: x['decimal_price'], reverse=True)

                moneylineTeam2array.sort(
                    key=lambda x: x['decimal_price'], reverse=True)

                """APPENDS ODDS DATA FOR THAT GAME"""
                odds_data = [
                    {f'{game_id}-spreadTeam1': spreadTeam1array}, 
                    {f'{game_id}-spreadTeam2': spreadTeam2array}, 
                    {f'{game_id}-over': overarray}, 
                    {f'{game_id}-under': underarray},
                    {f'{game_id}-moneylineTeam1': moneylineTeam1array},
                    {f'{game_id}-moneylineTeam2': moneylineTeam2array}
                ]

                game = {
                    'game_id': game_id,
                    'date_and_time': date_and_time,
                    'team_name_1': game_data.get('team1Name'),
                    'team_id_1': game_data.get('team1ID'),
                    'team_initials_1': game_data.get('team1Initials'),
                    'team_city_1': game_data.get('team1City'),
                    'team_name_2': game_data.get('team2Name'),
                    'team_id_2': game_data.get('team2ID'),
                    'team_initials_2': game_data.get('team2Initials'),
                    'team_city_2': game_data.get('team2City'),
                    'league': league,
                    'league_code': game_data.get('leagueCode'),
                    'odds': odds_data,
                    'end_date': None,
                    'team1score': None,
                    'team2score': None,
                    'time_left': None
                }
                
                data.append(game)
                
                game_odds_data = [
                    {f'spreadTeam1': spreadTeam1array}, 
                    {f'spreadTeam2': spreadTeam2array}, 
                    {f'over': overarray}, 
                    {f'under': underarray},
                    {f'moneylineTeam1': moneylineTeam1array},
                    {f'moneylineTeam2': moneylineTeam2array}
                ]
                
                game["odds"] = game_odds_data
                try:
                    rd.set(
                        "odds:" + \
                        str(game['league']) + \
                        ':' + str(game['league_code']) + \
                        ':' + str(game['date_and_time']) + \
                        ':' + str(game_id), str(game)
                    )
                    socketio.emit("update_odds", (str(game_id), str(game)), to="game_" + str(game_id))
                except Exception as e:
                    print(f"Error saving game data: {e}")


        # sorts the games by date and time with closest to occur games at the top
        data.sort(key=lambda x: x['date_and_time'])

        all_league_data.append({league: data})

    # Update scores if there's any
    scores = update_scores(app, db)

    try:
        rd.set('odds', str(all_league_data))
        response = "Odds updated successfully"
        status = 201
    except Exception as e:
        response = f"Error saving odds: {e}"
        status = 422

    return response, status


def update_scores(app, db):
    """Endpoint to update scores on Redis"""

    req = requests.get(
        f'https://scrimmage.api.areyouwatchingthis.com/api/games.json?apiKey={META_KEY}'
    )
    data = req.json().get('results')

    scores_data = []
    for d in data:

        gameID = d.get("gameID")
        team_1_score = d.get('team1Score')
        time_left = d.get('timeLeft')
        end_date = None

        if time_left == 'final':
            end_date = int(datetime.now().replace(microsecond=0).timestamp())

        # Saving all scores - even future games
        scores = {
            'gameID': gameID,
            'team1score': team_1_score,
            'team2score': d.get("team2Score"),
            'time_left': time_left,
            'end_date': end_date
        }           

        scores_data.append(scores)

        try:
            update_game_score(scores, app, db)
        except Exception as e:
            print(f"Error saving scores data: {e}")

    try:
        rd.set('scores', str(scores_data))
    except Exception as e:
        response = f"Error saving scores: {e}"
        status = 422
        return response, status

    return scores_data


def update_game_score(scores, app, db):
    """Update game with scores info"""
    
    try:
        keys = rd.keys(f"odds:*:*:*{str(scores['gameID'])}")
        for key in keys:
            game = rd.get(key)
            if game:
                game_str = game.decode("utf-8")
                game_json = ast.literal_eval(game_str)
                
                calculate_closing_line_value(game_json, scores, app, db)

                game_json['team1score'] = scores['team1score']
                game_json['team2score'] = scores['team2score']
                game_json['time_left'] = scores['time_left']
                game_json['end_date'] = scores['end_date']

                rd.set(key, str(game_json))
                socketio.emit("update_odds", (str(scores['gameID']), str(game_json)), to="game_" + str(scores['gameID']))
                print(f"Game updated successfully! {scores['gameID']}")
            else:
                continue
    except Exception as e:
        print(f"Error updating game score: {e}")


def calculate_closing_line_value(game, scores, app, db):
    if game['end_date'] == None and scores['end_date'] != None:
        with app.app_context():
            bets = UserBet.query.filter(UserBet.active_wager==True, UserBet.game_id==scores['gameID']).all()
            
            for bet in bets:
                bet_json = bet.as_dict()
                handicap = bet_json['handicap']
                decimal_price = bet_json['decimal_odds']
                odd_type = bet_json['odd_type']
                
                if handicap and odd_type == OddsTypeEnum.odds.value:
                    odd = list(filter(lambda odd: bet_json['bet_type'] in odd.keys(), game['odds']))
                    
                    if len(odd) > 0:
                        odd = odd[0][bet_json['bet_type']]  
                        specific_odd = list(filter(lambda odd: odd.get('book') == bet_json['sportsbook'], odd))

                        if len(specific_odd) > 0:
                            if specific_odd[0].get("handicap") == handicap:
                                closing_line = (1 / specific_odd[0].get("decimal_price") - (1 / decimal_price)) / (1 / decimal_price)
                                bet.closing_line_value = closing_line
                                socketio.emit("closing_line", json.dumps(bet_json), to="user_" + str(bet_json['user_id']))
                elif handicap and odd_type == OddsTypeEnum.side_odds.value:
                    team_id = str(bet_json['team_id']) if bet_json['team_id'] else 'any'
                    game_id = str(bet_json['game_id']) if bet_json['game_id'] else 'any'
                    player_id = str(bet_json['player_id']) if bet_json['player_id'] else 'any'
                    game_state_keys = rd.keys(pattern=odd_type  + "*" + bet_json['bet_type'] + "*" + game_id + "*" + team_id + "*" + player_id)
                    if len(game_state_keys) < 1:
                        continue
                    game_state = rd.get(game_state_keys[0])
                    data_str = game_state.decode("utf-8")
                    game_state = ast.literal_eval(data_str)
                    
                    game_odds = game_state['bet_for'] if bet_json['bet_for'] else game_state['bet_against']

                    specific_odd = list(filter(lambda odd: odd.get('provider') == bet_json['sportsbook'], game_odds))

                    if len(specific_odd) > 0:
                        if specific_odd[0].get("handicap") == handicap:
                            closing_line = (1 / specific_odd[0].get("price") - (1 / decimal_price)) / (1 / decimal_price)
                            bet.closing_line_value = closing_line
                            socketio.emit("closing_line", json.dumps(bet_json), to="user_" + str(bet_json['user_id']))                  
                    
            db.session.commit()


def update_side_odds():
    """Endpoint to update side odds on Redis"""
    
    start = time.time()
    
    games_data = get_all_leagues()
    
    for game_data in games_data:
        game_code = list(game_data.keys())[0]
    
        for league in game_data[game_code]:
            parameters = {
                'leagueCode': league.get('code', 'ignore'),  # change back to gameID variable
                'apiKey': META_KEY,
            }
            
            try:
                req = requests.get(
                    f'https://scrimmage.static.api.areyouwatchingthis.com/api/sideodds.json?includeGameSpecificMarkets&',
                    params=parameters)

                data = req.json()
                results = data.get('results')
                players = data.get('players')
                teams = data.get('teams')
            except Exception as err:
                print("side_odds ERROR: " + err)
                continue
            else:
                
                for side_bet in results:
                    
                    bets = {}
                    
                    for bet in side_bet['sideOdds']:
                        game_id = str(bet.get("gameID", 'any'))
                        team_id = str(bet.get("teamID", 'any'))
                        player_id = str(bet.get("playerID", 'any'))
                        
                        if bet.get("provider", 'any') == 'CONSENSUS':
                            continue

                        if game_id not in bets:
                            bets[game_id] = {}
                        if team_id not in bets[game_id]:
                            bets[game_id][team_id] = {}
                        if player_id not in bets[game_id][team_id]:
                            bets[game_id][team_id][player_id] = []
                            

                        # if it is a single outcome bet it makes price1 that value for sorting later
                        if bet.get("price1", None) == None and bet.get("price", None) != None:
                            bet['price1'] = bet['price']

                        # if there are no prices we skip so we don't show the data
                        if bet.get("price1", None) == None and bet.get("price2", None) == None:
                            continue
                        
                        if bet.get("price2", None) == 1:
                            del bet["price2"]
                            
                        bet['handicap'] = bet.get('value')
                        bet['title'] = side_bet.get('title')
                        # TODO: add player name and surname
                        
                        if player_id != 'any':
                            player_info = list(filter(lambda player: str(player.get('playerID')) == player_id, players))
                            if len(player_info) > 0:
                                bet['player_info'] = player_info[0]
                            else:
                                bet['player_info'] = {}
                        if team_id != 'any':
                            team_info = list(filter(lambda team: str(team.get('teamID')) == team_id, teams))
                            if len(team_info) > 0:
                                bet['team_info'] = team_info[0]
                            else:
                                bet['team_info'] = {}
                                
                        if bet.get('value'):
                            del bet['value']
                        
                        bets[game_id][team_id][player_id].append(bet)
                        
                    for game_id, listings in bets.items():
                        type = 'side_odds'
                        if game_id == 'any':
                            type = 'futures'
                        for team_id, players_list in listings.items():
                            for player_id, bets in players_list.items():
                                
                                # print(len(bets))
                                bets_for = []
                                bets_against = []
                                
                                for bet in bets:
                                    if bet.get('price1', None):
                                        new_bet = bet.copy()
                                        if bet.get('price2', None):
                                            del new_bet['price2']
                                        new_bet['price'] = new_bet['price1']
                                        del new_bet['price1']
                                        bets_for.append(new_bet)
                                    if bet.get('price2', None):
                                        new_bet = bet.copy()
                                        if bet.get('price1', None):
                                            del new_bet['price1']
                                        new_bet['price'] = new_bet['price2']
                                        del new_bet['price2']
                                        bets_against.append(new_bet)
                                        
                                bets_for.sort(reverse=True, key=lambda odd: odd.get('price', None))
                                bets_against.sort(reverse=True, key=lambda odd: odd.get('price', None))
                                
                                bets = {
                                    "bet_for": bets_for,
                                    "bet_against": bets_against,
                                }
                                    
                                rd.set(type + ":" + game_code + ":" + league['code'] + ":" + side_bet['type'] + ":" + game_id + ":" + team_id + ":" + player_id, str(bets))
                                
                                if type == 'side_odds':
                                    socketio.emit("update_side_odds", (str(game_id), str(bets)), to="game_" + str(game_id))
                                else:
                                    socketio.emit("update_futures", (str(league['code']), str(bets)), to="league_" + str(league['code']))
    
    end = time.time()
    print("\n" + "update_side_odds execution time: " + str(end - start) + "\n")
                
            
def get_all_leagues():
    
    with open(os.path.join('app/betting/json_scripts', 'league_codes.json'), 'r') as file:
        games_data = json.load(file).get('data')
            
    
        return games_data


def delete_inactive_games():
    """Erase game ended for 2+ days"""

    try:
        now = int(datetime.now().replace(microsecond=0).timestamp())
        today = datetime.fromtimestamp(now)

        key = "odds:*:*:*:*"
        keys = rd.keys(pattern=key)

        for key in keys:
            game = rd.get(key)
            game_str = game.decode("utf-8")
            game_json = ast.literal_eval(game_str)

            end_date = datetime.fromtimestamp(game_json['end_date'])
            result = dateutil.relativedelta.relativedelta(today, end_date)
            days = result.days

            if days >= 2:
                rd.delete(key)
                print("Game removed successfully!")
    except Exception as e:
        print(f"Error deleting game: {e}")
