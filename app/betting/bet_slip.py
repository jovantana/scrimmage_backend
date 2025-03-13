from app.authentication.jwt_auth import token_required
from flask import Blueprint, request
from flask_cors import cross_origin
from app.models import UserBet, db

# only submit info -- not able to edit or delete
# rerenders new form auto

bet_slip_bp = Blueprint('bet_slip', __name__, url_prefix='/bets')


@bet_slip_bp.route('/betlog', methods=['GET'])
@token_required
def get_bet_slip(current_user):
    """Endpoint to list user bets"""

    active_wager = request.args.get('active_wager')

    if active_wager:
        bets = UserBet.query.filter(
            UserBet.user_id==current_user.id,
            UserBet.active_wager==active_wager
        ).all()  
    else:
        bets = UserBet.query.filter(UserBet.user_id==current_user.id).all()  
    
    bets_json = [bet.as_dict() for bet in bets]    

    if bets_json:
        response = {'data': bets_json}
        return response, 200
    else:
        return "No data available", 203


# TODO: check out error -> Error on POST: 'results' is an invalid keyword argument for UserBet
@bet_slip_bp.route('/trackbet', methods=['POST'])
@token_required
def post_bet_slip(current_user):
    """Endpoint to save user bets"""

    body = request.get_json()
    try:
        user_bet = UserBet(
            event = body["event"],
            american_odds = body["american_odds"],
            decimal_odds = body["decimal_odds"],
            stake = body["stake"],
            sportsbook = body["sportsbook"],
            handicap = body.get("handicap", None),
            notification_handicap = body.get("notification_handicap", None),
            notification_price = body.get("notification_price", None),
            notification_completed = body.get("notification_completed", True), # This should be TRUE if user don't have notification enables
            closing_line_value = body.get("closing_line_value", None),
            roi = body.get("roi", None),
            result = body.get("result", None),
            payout = body.get("payout", None),
            game_date = body["game_date"],
            bet_date = body["bet_date"],
            user_id = current_user.id,
            game_id = body.get("game_id", None),
            league = body["league"],
            bet_type = body["bet_type"],
            odd_type = body ["odd_type"],
            team_id = body.get("team_id", None),
            player_id = body.get("player_id", None),
            bet_for = body.get("bet_for", True),
            active_wager = body.get("active_wager", False),
        )

        db.session.add(user_bet)
        db.session.commit()

        user_bet_json = user_bet.as_dict()

        response = {
            'mesage': "Bet saved succesfully!",
            'data': {
                'bet_id': user_bet_json['id'],
                'game_id': user_bet_json['game_id']
            }
        }

        return response, 201
    except Exception as e:
        return f"Error on POST: {e}", 400
