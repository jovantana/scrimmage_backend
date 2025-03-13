from app.betting.tests import game_over_odds_test, notifications_odds_test, side_odds_game_result_json
from app.models import OddsTypeEnum, ResultsEnum, SideBetTypeFormulas, UserBet
from app.config import rd, socketio, META_KEY
import json
from flask_socketio import join_room
import ast
import requests

def check_updates(app, db):
    print("check updates")
    # notifications_odds_test()
    with app.app_context():
        bets = UserBet.query.filter(UserBet.notification_completed==False).all()
        for bet in bets:
            odd_type = bet.odd_type
            game_state = None
            
            if odd_type == OddsTypeEnum.odds:
                game_state_keys = rd.keys("odds:*" + str(bet.game_id))
                game_state = rd.get(game_state_keys[0])
            elif odd_type == OddsTypeEnum.side_odds:
                team_id = str(bet.team_id) if bet.team_id else 'any'
                game_id = str(bet.game_id)
                player_id = str(bet.player_id) if bet.player_id else 'any'
                
                game_state_keys = rd.keys(pattern=odd_type.value  + "*" + bet.bet_type + "*" + game_id + "*" + team_id + "*" + player_id)
                game_state = rd.get(game_state_keys[0])
            elif odd_type == OddsTypeEnum.futures:
                team_id = str(bet.team_id) if bet.team_id else 'any'
                player_id = str(bet.player_id) if bet.player_id else 'any'
                
                game_state_keys = rd.keys(pattern=odd_type.value + "*" + bet.bet_type + "*" + team_id + "*" + player_id)
                game_state = rd.get(game_state_keys[0])
            if not game_state:
                continue
            
            data_str = game_state.decode("utf-8")
            game_state = ast.literal_eval(data_str)
            odds = []
            
            if odd_type == OddsTypeEnum.odds:
                odds = [odd_type_array[bet.bet_type] for odd_type_array in game_state['odds'] if bet.bet_type in odd_type_array][0]
            elif odd_type == OddsTypeEnum.side_odds or odd_type == OddsTypeEnum.futures:
                odds = []
                
                if bet.bet_for:
                    odds = game_state['bet_for']
                else:
                    odds = game_state['bet_against']
                
            send_notification_price_check = False
            send_notification_handicap_check = []
            
            for odd in odds:
                
                game_handicap = odd.get('handicap', -1)
                game_price = odd.get('decimal_price', odd.get('price', -1))

                if game_handicap == bet.notification_handicap and game_price >= bet.notification_price:
                    send_notification_price_check = True
                    break
                if bet.odd_type == OddsTypeEnum.odds:
                    if bet.bet_type == 'spreadTeam1' or bet.bet_type == 'spreadTeam2' or bet.bet_type == 'over':
                        if game_handicap > bet.notification_handicap:
                            send_notification_handicap_check.append(True)
                        else:
                            send_notification_handicap_check.append(False)
                    elif bet.bet_type == 'under':
                        if game_handicap < bet.notification_handicap:
                            send_notification_handicap_check.append(True)
                        else:
                            send_notification_handicap_check.append(False)
                if bet.odd_type == OddsTypeEnum.side_odds:
                    if bet.handicap and bet.bet_for:
                        if game_handicap > bet.notification_handicap:
                            send_notification_handicap_check.append(True)
                        else:
                            send_notification_handicap_check.append(False)
                    elif bet.handicap and not bet.bet_for:
                        if game_handicap < bet.notification_handicap:
                            send_notification_handicap_check.append(True)
                        else:
                            send_notification_handicap_check.append(False)
                
            if send_notification_price_check or all(send_notification_handicap_check):
                print("NOTIFICATION")
                bet.notification_completed = True
                bet_json = bet.as_dict()
                socketio.emit("notification", json.dumps(bet_json), to="user_" + str(bet_json['user_id']))
                db.session.commit()

def check_game_over(app, db):
    print('check_game_over')
    #game_over_odds_test()
    with app.app_context():
        bets = UserBet.query.filter(UserBet.active_wager==True).all()
        for bet in bets:

            game_state_keys = rd.keys("odds:*" + str(bet.game_id))
            if len(game_state_keys) < 1:
                continue
            game_state = rd.get(game_state_keys[0])
            if not game_state:
                print("NO GAME STATE")
                continue

            data_str = game_state.decode("utf-8")
            game_state = ast.literal_eval(data_str)
                  
            if game_state.get('time_left', None)=='Final':
                
                # Calculate result
                
                try:
                    if bet.odd_type == OddsTypeEnum.odds:
                        bet.result = SideBetTypeFormulas.calculate_result(bet.bet_type)(game_state['team1score'], game_state['team2score'], bet.handicap)
                        print(bet.result)
                    elif bet.odd_type == OddsTypeEnum.side_odds:
                        variables = SideBetTypeFormulas.bet_type_variables(bet.bet_type)
                        
                        parameters = {
                            'gameID': bet.game_id,
                            'apiKey': META_KEY
                        }

                        req = requests.get(
                            f'https://scrimmage.api.areyouwatchingthis.com/api/sideodds.json?',
                            params=parameters)
                        
                        # checks to see if there are results at all

                        results = req.json().get('results')
                        
                        # results = side_odds_game_result_json['results']
                        
                        if not results:
                            continue
                        statistic = results[0]['statistics']
                        
                        variables_data = []
                        
                        for _, bet_types in statistic.items():
                            
                            for variable in variables:
                                players = bet_types[variable]
                                for player in players:
                                    if player['playerID'] == bet.player_id:
                                        variables_data.append(player['value'])
                        
                        bet.result = SideBetTypeFormulas.calculate_result(bet.bet_type)(*variables_data, bet.bet_for, bet.handicap)
                        print(bet.result) 
                    # Calculate payout
                    
                    if bet.result == ResultsEnum.win:
                        bet.payout = (bet.decimal_odds - 1) * bet.stake
                        bet.roi = bet.payout / bet.stake
                    elif bet.result == ResultsEnum.loss:
                        bet.payout = 0 - bet.stake
                        bet.roi = bet.payout / bet.stake
                    else:
                        bet.payout = 0
                        bet.roi = 0
                except Exception as err:
                    print("Error during check_game_over: " + err)
                # Send notification to frontend
                
                bet.active_wager = False
                bet_json = bet.as_dict()
                print("GAME " + str(bet.game_id) + " is over")
                socketio.emit("bet_results", json.dumps(bet_json), to="user_" + str(bet_json['user_id']))
            
            bet.notification_completed = True
            db.session.commit()
