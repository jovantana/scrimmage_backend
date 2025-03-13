import enum
import re
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.orm import backref, validates
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime, timedelta

db = SQLAlchemy()


class FiltersEnum(enum.Enum):
    __tablename__ = 'filters'

    football = "football"
    basketball = "basketball"
    baseball = "baseball"
    hockey = "hockey"
    soccer = "soccer"
    fighting = "fighting"
    tennis = "tennis"
    golf = "golf"
    esports = "esports"  

    @staticmethod
    def as_list():
        return [
            FiltersEnum.football.value, 
            FiltersEnum.basketball.value,
            FiltersEnum.baseball.value,
            FiltersEnum.hockey.value,
            FiltersEnum.soccer.value,
            FiltersEnum.fighting.value,
            FiltersEnum.tennis.value,
            FiltersEnum.golf.value,
            FiltersEnum.esports.value
        ]


class ResultsEnum(enum.Enum):
    __tablename__ = 'results'

    win = "win"
    loss = "loss"
    push = "push"
    cancelled = "cancelled"

    @staticmethod
    def as_list():
        return [
            ResultsEnum.win.value,
            ResultsEnum.loss.value,
            ResultsEnum.push.value,
            ResultsEnum.cancelled.value
        ]


# variables = BetTypeEnum.bet_type_variables(bet_type)
# variables_data = game_score_data.find(variables)
# result = BetTypeEnum.calculate_result(bet_type)(variables_data, bet_for, handicap)
class SideBetTypeFormulas():
    @staticmethod
    def bet_type_variables(bet_type):
        return {
            "NBA_GAME_PLAYER_POINTS": ["BASKETBALL_POINTS"],
            "NBA_GAME_PLAYER_REBOUNDS": ["BASKETBALL_REBOUNDS_OFFENSIVE", "BASKETBALL_REBOUNDS_DEFENSIVE"],
            "NBA_GAME_PLAYER_ASSISTS": ["BASKETBALL_ASSISTS"],
            "NBA_GAME_PLAYER_BLOCKS": ["BASKETBALL_BLOCKS"],
            "NBA_GAME_PLAYER_STEALS": ["BASKETBALL_STEALS"],
            "NBA_GAME_PLAYER_TURNOVERS": ["BASKETBALL_TURNOVERS"],
            "NBA_GAME_PLAYER_POINTS_REBOUNDS": ["BASKETBALL_POINTS", "BASKETBALL_REBOUNDS_OFFENSIVE",
                                                "BASKETBALL_REBOUNDS_DEFENSIVE"],
            "NBA_GAME_PLAYER_POINTS_ASSISTS": ["BASKETBALL_POINTS", "BASKETBALL_ASSISTS"],
            "NBA_GAME_PLAYER_REBOUNDS_ASSISTS": ["BASKETBALL_REBOUNDS_OFFENSIVE", "BASKETBALL_REBOUNDS_DEFENSIVE",
                                                 "BASKETBALL_ASSISTS"],
            "NBA_GAME_PLAYER_STEALS_BLOCKS": ["BASKETBALL_STEALS", "BASKETBALL_BLOCKS"],
            "NBA_GAME_PLAYER_POINTS_REBOUNDS_ASSISTS": ["BASKETBALL_POINTS", "BASKETBALL_REBOUNDS_OFFENSIVE",
                                                        "BASKETBALL_REBOUNDS_DEFENSIVE", "BASKETBALL_ASSISTS"],
            "NBA_GAME_PLAYER_3_POINTERS_MADE": ["BASKETBALL_THREE_POINTERS_MADE"],
            "NBA_GAME_PLAYER_DOUBLE_DOUBLE": ["BASKETBALL_REBOUNDS_OFFENSIVE", "BASKETBALL_REBOUNDS_DEFENSIVE",
                                              "BASKETBALL_ASSISTS", "BASKETBALL_POINTS", "BASKETBALL_STEALS",
                                              "BASKETBALL_BLOCKS"],
            "NBA_GAME_PLAYER_TRIPLE_DOUBLE": ["BASKETBALL_REBOUNDS_OFFENSIVE", "BASKETBALL_REBOUNDS_DEFENSIVE",
                                              "BASKETBALL_ASSISTS", "BASKETBALL_POINTS", "BASKETBALL_STEALS",
                                              "BASKETBALL_BLOCKS"],
            "NFL_GAME_PLAYER_PASSING_YARDS": ["FOOTBALL_PASSING_YARDS"],
            "NFL_GAME_PLAYER_PASSING_TOUCHDOWNS": ["FOOTBALL_PASSING_TOUCHDOWNS"],
            "NFL_GAME_PLAYER_PASSING_ATTEMPTS": ["FOOTBALL_PASSING_ATTEMPTS"],
            "NFL_GAME_PLAYER_PASSING_COMPLETIONS": ["FOOTBALL_PASSING_COMPLETIONS"],
            "NFL_GAME_PLAYER_PASSING_INTERCEPTIONS": ["FOOTBALL_PASSING_INTERCEPTIONS"],
            "NFL_GAME_PLAYER_RUSHING_YARDS": ["FOOTBALL_RUSHING_YARDS"],
            "NFL_GAME_PLAYER_RUSHING_TOUCHDOWNS": ["FOOTBALL_RUSHING_TOUCHDOWNS"],
            "NFL_GAME_PLAYER_RUSHING_ATTEMPTS": ["FOOTBALL_RUSHING_ATTEMPTS"],
            "NFL_GAME_PLAYER_RUSHING_LONG": ["FOOTBALL_RUSHING_LONG"],
            "NFL_GAME_PLAYER_RECEIVING_YARDS": ["FOOTBALL_RECEIVING_YARDS"],
            "NFL_GAME_PLAYER_RECEIVING_TOUCHDOWNS": ["FOOTBALL_RECEIVING_TOUCHDOWNS"],
            "NFL_GAME_PLAYER_RECEIVING_RECEPTIONS": ["FOOTBALL_RECEIVING_RECEPTIONS"],
            "NFL_GAME_PLAYER_RECEIVING_LONG": ["FOOTBALL_RECEIVING_LONG"],
            "NFL_GAME_PLAYER_PASSING_RUSHING_YARDS": ["FOOTBALL_PASSING_YARDS", "FOOTBALL_RUSHING_YARDS"],
            "NFL_GAME_PLAYER_RUSHING_RECEIVING_YARDS": ["FOOTBALL_RUSHING_YARDS", "FOOTBALL_RECEIVING_YARDS"],
            "NFL_GAME_PLAYER_SCORE_TOUCHDOWN": ["FOOTBALL_RUSHING_TOUCHDOWNS", "FOOTBALL_RECEIVING_TOUCHDOWNS"],
            "NFL_GAME_PLAYER_SCORE_TWO_TOUCHDOWNS": ["FOOTBALL_RUSHING_TOUCHDOWNS", "FOOTBALL_RECEIVING_TOUCHDOWNS"],
            "NFL_GAME_PLAYER_SCORE_THREE_TOUCHDOWNS": ["FOOTBALL_RUSHING_TOUCHDOWNS", "FOOTBALL_RECEIVING_TOUCHDOWNS"],
            "MLB_GAME_PLAYER_PITCHER_STRIKEOUTS": ["BASEBALL_PITCHING_STRIKEOUTS"],
            "MLB_GAME_PLAYER_PITCHER_ALLOWED_EARNED_RUNS": ["BASEBALL_PITCHING_RUNS_EARNED"],
            "MLB_GAME_PLAYER_PITCHER_ALLOWED_HITS": ["BASEBALL_PITCHING_HITS"],
            "MLB_GAME_PLAYER_HOME_RUN": ["BASEBALL_BATTING_HOME_RUNS"],
            "MLB_GAME_PLAYER_HOME_RUNS": ["BASEBALL_BATTING_HOME_RUNS"],
            "MLB_GAME_PLAYER_HITS": ["BASEBALL_BATTING_HITS"],
            "MLB_GAME_PLAYER_HIT": ["BASEBALL_BATTING_HITS"],
            "MLB_GAME_PLAYER_HITS_AT_LEAST_TWO": ["BASEBALL_BATTING_HITS"],
            "MLB_GAME_PLAYER_HITS_AT_LEAST_THREE": ["BASEBALL_BATTING_HITS"],
            "MLB_GAME_PLAYER_HITS_AT_LEAST_FOUR": ["BASEBALL_BATTING_HITS"],
            "MLB_GAME_PLAYER_STRIKEOUTS": ["BASEBALL_BATTING_STRIKEOUTS"],
            "MLB_GAME_PLAYER_SINGLES": ["FOOTBALL_RUSHING_TOUCHDOWNS", "FOOTBALL_RECEIVING_TOUCHDOWNS"],
            "MLB_GAME_PLAYER_DOUBLES": ["BASEBALL_BATTING_DOUBLES"],
            "MLB_GAME_PLAYER_TRIPLES": ["BASEBALL_BATTING_TRIPLES"],
            "MLB_GAME_PLAYER_BASES": ["BASEBALL_BATTING_HITS", "BASEBALL_BATTING_HOME_RUNS", "BASEBALL_BATTING_TRIPLES",
                                      "BASEBALL_BATTING_DOUBLES"],
            "MLB_GAME_PLAYER_RUNS_SCORED": ["BASEBALL_BATTING_RUNS"],
            "MLB_GAME_PLAYER_RBIS": ["BASEBALL_BATTING_RUNS_BATTED_IN"],
            "MLB_GAME_PLAYER_RBI": ["BASEBALL_BATTING_RUNS_BATTED_IN"],
        }[bet_type]

    @staticmethod
    def calculate_result(bet_type):
        return {
            "spreadTeam1": lambda team1score, team2score, handicap: SideBetTypeFormulas._result('spread', True,
                                                                                                team2score - team1score,
                                                                                                handicap),
            "spreadTeam2": lambda team1score, team2score, handicap: SideBetTypeFormulas._result('spread', True,
                                                                                                team1score - team2score,
                                                                                                handicap),
            "moneylineTeam1": lambda team1score, team2score, handicap: SideBetTypeFormulas._result('moneyline', True,
                                                                                                   team1score,
                                                                                                   team2score),
            "moneylineTeam2": lambda team1score, team2score, handicap: SideBetTypeFormulas._result('moneyline', True,
                                                                                                   team2score,
                                                                                                   team1score),
            "over": lambda team1score, team2score, handicap: SideBetTypeFormulas._result('totals', True,
                                                                                         team1score + team2score,
                                                                                         handicap),
            "under": lambda team1score, team2score, handicap: SideBetTypeFormulas._result('totals', False,
                                                                                          team1score + team2score,
                                                                                          handicap),
            "NBA_GAME_PLAYER_POINTS": lambda BASKETBALL_POINTS, bet_for, handicap: SideBetTypeFormulas._result('totals',
                                                                                                               bet_for,
                                                                                                               BASKETBALL_POINTS,
                                                                                                               handicap),
            "NBA_GAME_PLAYER_REBOUNDS": lambda BASKETBALL_REBOUNDS_OFFENSIVE, BASKETBALL_REBOUNDS_DEFENSIVE, bet_for,
                                               handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                     BASKETBALL_REBOUNDS_OFFENSIVE + BASKETBALL_REBOUNDS_DEFENSIVE,
                                                                                     handicap),
            "NBA_GAME_PLAYER_ASSISTS": lambda BASKETBALL_ASSISTS, bet_for, handicap: SideBetTypeFormulas._result(
                'totals', bet_for, BASKETBALL_ASSISTS, handicap),
            "NBA_GAME_PLAYER_BLOCKS": lambda BASKETBALL_BLOCKS, bet_for, handicap: SideBetTypeFormulas._result('totals',
                                                                                                               bet_for,
                                                                                                               BASKETBALL_BLOCKS,
                                                                                                               handicap),
            "NBA_GAME_PLAYER_STEALS": lambda BASKETBALL_STEALS, bet_for, handicap: SideBetTypeFormulas._result('totals',
                                                                                                               bet_for,
                                                                                                               BASKETBALL_STEALS,
                                                                                                               handicap),
            "NBA_GAME_PLAYER_TURNOVERS": lambda BASKETBALL_TURNOVERS, bet_for, handicap: SideBetTypeFormulas._result(
                'totals', bet_for, BASKETBALL_TURNOVERS, handicap),
            "NBA_GAME_PLAYER_POINTS_REBOUNDS": lambda BASKETBALL_POINTS, BASKETBALL_REBOUNDS_OFFENSIVE,
                                                      BASKETBALL_REBOUNDS_DEFENSIVE, bet_for,
                                                      handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                            BASKETBALL_POINTS + BASKETBALL_REBOUNDS_OFFENSIVE + BASKETBALL_REBOUNDS_DEFENSIVE,
                                                                                            handicap),
            "NBA_GAME_PLAYER_POINTS_ASSISTS": lambda BASKETBALL_POINTS, BASKETBALL_ASSISTS, bet_for,
                                                     handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                           BASKETBALL_POINTS + BASKETBALL_ASSISTS,
                                                                                           handicap),
            "NBA_GAME_PLAYER_REBOUNDS_ASSISTS": lambda BASKETBALL_REBOUNDS_OFFENSIVE, BASKETBALL_REBOUNDS_DEFENSIVE,
                                                       BASKETBALL_ASSISTS, bet_for,
                                                       handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                             BASKETBALL_REBOUNDS_OFFENSIVE + BASKETBALL_REBOUNDS_DEFENSIVE + BASKETBALL_ASSISTS,
                                                                                             handicap),
            "NBA_GAME_PLAYER_STEALS_BLOCKS": lambda BASKETBALL_STEALS, BASKETBALL_BLOCKS, bet_for,
                                                    handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                          BASKETBALL_STEALS + BASKETBALL_BLOCKS,
                                                                                          handicap),
            "NBA_GAME_PLAYER_POINTS_REBOUNDS_ASSISTS": lambda BASKETBALL_POINTS, BASKETBALL_REBOUNDS_OFFENSIVE,
                                                              BASKETBALL_REBOUNDS_DEFENSIVE, BASKETBALL_ASSISTS,
                                                              bet_for, handicap: SideBetTypeFormulas._result('totals',
                                                                                                             bet_for,
                                                                                                             BASKETBALL_POINTS + BASKETBALL_REBOUNDS_OFFENSIVE + BASKETBALL_REBOUNDS_DEFENSIVE + BASKETBALL_ASSISTS,
                                                                                                             handicap),
            "NBA_GAME_PLAYER_3_POINTERS_MADE": lambda BASKETBALL_THREE_POINTERS_MADE, bet_for,
                                                      handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                            BASKETBALL_THREE_POINTERS_MADE,
                                                                                            handicap),
            "NBA_GAME_PLAYER_DOUBLE_DOUBLE": lambda BASKETBALL_REBOUNDS_OFFENSIVE, BASKETBALL_REBOUNDS_DEFENSIVE,
                                                    BASKETBALL_ASSISTS, BASKETBALL_POINTS, BASKETBALL_STEALS,
                                                    BASKETBALL_BLOCKS, bet_for, handicap: SideBetTypeFormulas._result(
                'strong_moneyline', bet_for, len(list(filter((10).__le__, [
                    BASKETBALL_REBOUNDS_OFFENSIVE + BASKETBALL_REBOUNDS_DEFENSIVE, BASKETBALL_ASSISTS,
                    BASKETBALL_POINTS, BASKETBALL_STEALS, BASKETBALL_BLOCKS]))), 2),
            "NBA_GAME_PLAYER_TRIPLE_DOUBLE": lambda BASKETBALL_REBOUNDS_OFFENSIVE, BASKETBALL_REBOUNDS_DEFENSIVE,
                                                    BASKETBALL_ASSISTS, BASKETBALL_POINTS, BASKETBALL_STEALS,
                                                    BASKETBALL_BLOCKS, bet_for, handicap: SideBetTypeFormulas._result(
                'strong_moneyline', bet_for, len(list(filter((10).__le__, [
                    BASKETBALL_REBOUNDS_OFFENSIVE + BASKETBALL_REBOUNDS_DEFENSIVE, BASKETBALL_ASSISTS,
                    BASKETBALL_POINTS, BASKETBALL_STEALS, BASKETBALL_BLOCKS]))), 3),
            "NFL_GAME_PLAYER_PASSING_YARDS": lambda FOOTBALL_PASSING_YARDS, bet_for,
                                                    handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                          FOOTBALL_PASSING_YARDS,
                                                                                          handicap),
            "NFL_GAME_PLAYER_PASSING_TOUCHDOWNS": lambda FOOTBALL_PASSING_TOUCHDOWNS, bet_for,
                                                         handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                               FOOTBALL_PASSING_TOUCHDOWNS,
                                                                                               handicap),
            "NFL_GAME_PLAYER_PASSING_ATTEMPTS": lambda FOOTBALL_PASSING_ATTEMPTS, bet_for,
                                                       handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                             FOOTBALL_PASSING_ATTEMPTS,
                                                                                             handicap),
            "NFL_GAME_PLAYER_PASSING_COMPLETIONS": lambda FOOTBALL_PASSING_COMPLETIONS, bet_for,
                                                          handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                                FOOTBALL_PASSING_COMPLETIONS,
                                                                                                handicap),
            "NFL_GAME_PLAYER_PASSING_INTERCEPTIONS": lambda FOOTBALL_PASSING_INTERCEPTIONS, bet_for,
                                                            handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                                  FOOTBALL_PASSING_INTERCEPTIONS,
                                                                                                  handicap),
            "NFL_GAME_PLAYER_RUSHING_YARDS": lambda FOOTBALL_RUSHING_YARDS, bet_for,
                                                    handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                          FOOTBALL_RUSHING_YARDS,
                                                                                          handicap),
            "NFL_GAME_PLAYER_RUSHING_TOUCHDOWNS": lambda FOOTBALL_RUSHING_TOUCHDOWNS, bet_for,
                                                         handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                               FOOTBALL_RUSHING_TOUCHDOWNS,
                                                                                               handicap),
            "NFL_GAME_PLAYER_RUSHING_ATTEMPTS": lambda FOOTBALL_RUSHING_ATTEMPTS, bet_for,
                                                       handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                             FOOTBALL_RUSHING_ATTEMPTS,
                                                                                             handicap),
            "NFL_GAME_PLAYER_RUSHING_LONG": lambda FOOTBALL_RUSHING_LONG, bet_for,
                                                   handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                         FOOTBALL_RUSHING_LONG,
                                                                                         handicap),
            "NFL_GAME_PLAYER_RECEIVING_YARDS": lambda FOOTBALL_RECEIVING_YARDS, bet_for,
                                                      handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                            FOOTBALL_RECEIVING_YARDS,
                                                                                            handicap),
            "NFL_GAME_PLAYER_RECEIVING_TOUCHDOWNS": lambda FOOTBALL_RECEIVING_TOUCHDOWNS, bet_for,
                                                           handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                                 FOOTBALL_RECEIVING_TOUCHDOWNS,
                                                                                                 handicap),
            "NFL_GAME_PLAYER_RECEIVING_RECEPTIONS": lambda FOOTBALL_RECEIVING_RECEPTIONS, bet_for,
                                                           handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                                 FOOTBALL_RECEIVING_RECEPTIONS,
                                                                                                 handicap),
            "NFL_GAME_PLAYER_RECEIVING_LONG": lambda FOOTBALL_RECEIVING_LONG, bet_for,
                                                     handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                           FOOTBALL_RECEIVING_LONG,
                                                                                           handicap),
            "NFL_GAME_PLAYER_PASSING_RUSHING_YARDS": lambda FOOTBALL_PASSING_YARDS, FOOTBALL_RUSHING_YARDS, bet_for,
                                                            handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                                  FOOTBALL_PASSING_YARDS + FOOTBALL_RUSHING_YARDS,
                                                                                                  handicap),
            "NFL_GAME_PLAYER_RUSHING_RECEIVING_YARDS": lambda FOOTBALL_RUSHING_YARDS, FOOTBALL_RECEIVING_YARDS, bet_for,
                                                              handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                                    FOOTBALL_RUSHING_YARDS + FOOTBALL_RECEIVING_YARDS,
                                                                                                    handicap),
            "NFL_GAME_PLAYER_SCORE_TOUCHDOWN": lambda FOOTBALL_RUSHING_TOUCHDOWNS, FOOTBALL_RECEIVING_TOUCHDOWNS,
                                                      bet_for, handicap: SideBetTypeFormulas._result('strong_moneyline',
                                                                                                     bet_for,
                                                                                                     FOOTBALL_RUSHING_TOUCHDOWNS + FOOTBALL_RECEIVING_TOUCHDOWNS,
                                                                                                     1),
            "NFL_GAME_PLAYER_SCORE_TWO_TOUCHDOWNS": lambda FOOTBALL_RUSHING_TOUCHDOWNS, FOOTBALL_RECEIVING_TOUCHDOWNS,
                                                           bet_for, handicap: SideBetTypeFormulas._result(
                'strong_moneyline', bet_for, FOOTBALL_RUSHING_TOUCHDOWNS + FOOTBALL_RECEIVING_TOUCHDOWNS, 2),
            "NFL_GAME_PLAYER_SCORE_THREE_TOUCHDOWNS": lambda FOOTBALL_RUSHING_TOUCHDOWNS, FOOTBALL_RECEIVING_TOUCHDOWNS,
                                                             bet_for, handicap: SideBetTypeFormulas._result(
                'strong_moneyline', bet_for, FOOTBALL_RUSHING_TOUCHDOWNS + FOOTBALL_RECEIVING_TOUCHDOWNS, 3),
            "MLB_GAME_PLAYER_PITCHER_STRIKEOUTS": lambda BASEBALL_PITCHING_STRIKEOUTS, bet_for,
                                                         handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                               BASEBALL_PITCHING_STRIKEOUTS,
                                                                                               handicap),
            "MLB_GAME_PLAYER_PITCHER_ALLOWED_EARNED_RUNS": lambda BASEBALL_PITCHING_RUNS_EARNED, bet_for,
                                                                  handicap: SideBetTypeFormulas._result('totals',
                                                                                                        bet_for,
                                                                                                        BASEBALL_PITCHING_RUNS_EARNED,
                                                                                                        handicap),
            "MLB_GAME_PLAYER_PITCHER_ALLOWED_HITS": lambda BASEBALL_PITCHING_HITS, bet_for,
                                                           handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                                 BASEBALL_PITCHING_HITS,
                                                                                                 handicap),
            "MLB_GAME_PLAYER_HOME_RUN": lambda BASEBALL_BATTING_HOME_RUNS, bet_for,
                                               handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                     BASEBALL_BATTING_HOME_RUNS,
                                                                                     handicap),
            "MLB_GAME_PLAYER_HOME_RUNS": lambda BASEBALL_BATTING_HOME_RUNS, bet_for,
                                                handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                      BASEBALL_BATTING_HOME_RUNS,
                                                                                      handicap),
            "MLB_GAME_PLAYER_HITS": lambda BASEBALL_BATTING_HITS, bet_for, handicap: SideBetTypeFormulas._result(
                'totals', bet_for, BASEBALL_BATTING_HITS, handicap),
            "MLB_GAME_PLAYER_HIT": lambda BASEBALL_BATTING_HITS, bet_for, handicap: SideBetTypeFormulas._result(
                'strong_moneyline', bet_for, BASEBALL_BATTING_HITS, 1),
            "MLB_GAME_PLAYER_HITS_AT_LEAST_TWO": lambda BASEBALL_BATTING_HITS, bet_for,
                                                        handicap: SideBetTypeFormulas._result('strong_moneyline',
                                                                                              bet_for,
                                                                                              BASEBALL_BATTING_HITS, 2),
            "MLB_GAME_PLAYER_HITS_AT_LEAST_THREE": lambda BASEBALL_BATTING_HITS, bet_for,
                                                          handicap: SideBetTypeFormulas._result('strong_moneyline',
                                                                                                bet_for,
                                                                                                BASEBALL_BATTING_HITS,
                                                                                                3),
            "MLB_GAME_PLAYER_HITS_AT_LEAST_FOUR": lambda BASEBALL_BATTING_HITS, bet_for,
                                                         handicap: SideBetTypeFormulas._result('strong_moneyline',
                                                                                               bet_for,
                                                                                               BASEBALL_BATTING_HITS,
                                                                                               4),
            "MLB_GAME_PLAYER_STRIKEOUTS": lambda BASEBALL_BATTING_STRIKEOUTS, bet_for,
                                                 handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                       BASEBALL_BATTING_STRIKEOUTS,
                                                                                       handicap),
            "MLB_GAME_PLAYER_SINGLES": lambda FOOTBALL_RUSHING_TOUCHDOWNS, FOOTBALL_RECEIVING_TOUCHDOWNS, bet_for,
                                              handicap: SideBetTypeFormulas._result('strong_moneyline', bet_for,
                                                                                    FOOTBALL_RUSHING_TOUCHDOWNS + FOOTBALL_RECEIVING_TOUCHDOWNS,
                                                                                    2),
            "MLB_GAME_PLAYER_DOUBLES": lambda BASEBALL_BATTING_DOUBLES, bet_for, handicap: SideBetTypeFormulas._result(
                'totals', bet_for, BASEBALL_BATTING_DOUBLES, handicap),
            "MLB_GAME_PLAYER_TRIPLES": lambda BASEBALL_BATTING_TRIPLES, bet_for, handicap: SideBetTypeFormulas._result(
                'totals', bet_for, BASEBALL_BATTING_TRIPLES, handicap),
            "MLB_GAME_PLAYER_BASES": lambda BASEBALL_BATTING_HITS, BASEBALL_BATTING_HOME_RUNS, BASEBALL_BATTING_TRIPLES,
                                            BASEBALL_BATTING_DOUBLES, bet_for, handicap: SideBetTypeFormulas._result(
                'totals', bet_for,
                BASEBALL_BATTING_HITS - BASEBALL_BATTING_HOME_RUNS - BASEBALL_BATTING_TRIPLES - BASEBALL_BATTING_DOUBLES,
                handicap),
            "MLB_GAME_PLAYER_RUNS_SCORED": lambda BASEBALL_BATTING_RUNS, bet_for, handicap: SideBetTypeFormulas._result(
                'totals', bet_for, BASEBALL_BATTING_RUNS, handicap),
            "MLB_GAME_PLAYER_RBIS": lambda BASEBALL_BATTING_RUNS_BATTED_IN, bet_for,
                                           handicap: SideBetTypeFormulas._result('totals', bet_for,
                                                                                 BASEBALL_BATTING_RUNS_BATTED_IN,
                                                                                 handicap),
            "MLB_GAME_PLAYER_RBI": lambda BASEBALL_BATTING_RUNS_BATTED_IN, bet_for,
                                          handicap: SideBetTypeFormulas._result('strong_moneyline', bet_for,
                                                                                BASEBALL_BATTING_RUNS_BATTED_IN, 1),

        }[bet_type]

    @staticmethod
    def _result(type, bet_for, game_value, bet_value):
        if type == 'spread':
            if bet_value > game_value:
                return ResultsEnum.win
            elif bet_value < game_value:
                return ResultsEnum.loss
            else:
                return ResultsEnum.push
        # OVER
        if type == 'totals' and bet_for:
            if bet_value > game_value:
                return ResultsEnum.win
            elif bet_value < game_value:
                return ResultsEnum.loss
            else:
                return ResultsEnum.push
        # UNDER
        if type == 'totals' and not bet_for:
            if bet_value < game_value:
                return ResultsEnum.win
            elif bet_value > game_value:
                return ResultsEnum.loss
            else:
                return ResultsEnum.push
        elif type == 'moneyline' and bet_for:
            if game_value > bet_value:
                return ResultsEnum.win
            elif game_value < bet_value:
                return ResultsEnum.loss
            else:
                return ResultsEnum.push
        elif type == 'moneyline' and not bet_for:
            if game_value < bet_value:
                return ResultsEnum.win
            elif game_value > bet_value:
                return ResultsEnum.loss
            else:
                return ResultsEnum.push
        elif type == 'strong_moneyline' and bet_for:
            if game_value >= bet_value:
                return ResultsEnum.win
            else:
                return ResultsEnum.loss
        elif type == 'strong_moneyline' and not bet_for:
            if game_value < bet_value:
                return ResultsEnum.win
            else:
                return ResultsEnum.loss


class OddsTypeEnum(enum.Enum):
    __tablename__ = 'odd_types'
    odds = 'odds'
    side_odds = 'side_odds'
    futures = 'futures'

    @staticmethod
    def as_list():
        return [OddsTypeEnum.odds.value, OddsTypeEnum.side_odds.value, \
                OddsTypeEnum.futures.value]


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    username = db.Column(db.String, unique=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    subscribed_ids = db.Column(ARRAY(db.String), default=None, unique=False)  # blogs subscribed - saves author id
    newsfeed_filters = db.Column((ARRAY(ENUM(FiltersEnum))))
    light_mode = db.Column(db.Boolean, default=True)  # default light mode
    odds_format = db.Column(db.Boolean, default=True)  # default American
    stripe_id = db.Column(db.Integer, unique=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, onupdate=DateTime)

    user_bets = db.relationship('UserBet', backref='user', lazy='joined')
    author = db.relationship('Author', backref='user', lazy='joined')
    password = db.Column(db.String)
    dob = db.Column(db.Date)
    region = db.Column(db.String, nullable=True)

    # facebook
    facebook_user_id = db.Column(db.String, unique=True)
    facebook_long_live_token = db.Column(db.String, unique=True)

    # google
    google_user_id = db.Column(db.String, unique=True)
    google_user_token = db.Column(db.String, unique=True)

    @validates('username', 'name')
    def validate_required_fields(self, key, data):
        if not data:
            raise ValueError('{} is required'.format(key))
        if key == 'username':
            return data.lower()
        return data

    @validates('email', )
    def validate_email(self, key, data):
        if not data:
            raise ValueError('{} is required'.format(key))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", data):
            raise ValueError("Invalid Email Address")
        return data.lower()

    def __repr__(self):
        return '<User {}>'.format(self.as_dict())

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'subscribed_ids': self.subscribed_ids,
            'newsfeed_filters': list(map(lambda filter: filter.value, self.newsfeed_filters)) if self.newsfeed_filters else None,
            'light_mode': self.light_mode,
            'odds_format': self.odds_format,
            'dob': int(datetime.combine(self.dob, datetime.min.time()).timestamp()) if self.dob else None,
            'created_at': int(datetime.timestamp(self.created_at)) if self.created_at else None,
            'updated_at': int(datetime.timestamp(self.updated_at)) if self.updated_at else None
        }


class UserJwtToken(db.Model):
    __tablename__ = 'user_jwt_token'
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    jwt_token = db.Column(db.String, nullable=False, unique=True)
    refresh_token = db.Column(db.String, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    expire_time = db.Column(db.DateTime, nullable=False)
    refresh_expire_time = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def create(user):
        from app.authentication.jwt_auth import create_jwt_token
        expire_time = datetime.utcnow() + timedelta(days=7)
        refresh_expire_time = datetime.utcnow() + timedelta(days=30)
        jwt_token = create_jwt_token(user, expire_time)
        refresh_jwt_token = create_jwt_token(user, refresh_expire_time)
        token = UserJwtToken(jwt_token=jwt_token, user_id=user.id, expire_time=expire_time,
                             refresh_token=refresh_jwt_token, refresh_expire_time=refresh_expire_time)
        db.session.add(token)
        db.session.commit()
        return token

    def refresh_jwt_token(self):
        from app.authentication.jwt_auth import create_jwt_token
        user = User.query.filter_by(id=self.user_id).first()
        expire_time = datetime.utcnow() + timedelta(minutes=60)
        refresh_expire_time = datetime.utcnow() + timedelta(days=7)
        jwt_token = create_jwt_token(user, expire_time)
        refresh_jwt_token = create_jwt_token(user, refresh_expire_time)
        self.jwt_token = jwt_token
        self.expire_time = expire_time
        self.refresh_token = refresh_jwt_token
        self.refresh_expire_time = refresh_expire_time
        db.session.commit()
        return self

    def delete_token(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        return {'refresh_token': self.refresh_token, 'jwt_token': self.jwt_token, 'expire_in': 60*60}

    def user(self):
        return User.query.filter_by(id=self.user_id).first()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    subscribers = db.Column(ARRAY(db.String), default=[])  # array of user_id
    email_subscribers = db.Column(ARRAY(db.String), default=[])
    total_revenue = db.Column(db.Integer)  # ads + subscribers
    monthly_fee = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, onupdate=DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    posts = db.relationship('Post', backref='author', lazy='joined')

    def __repr__(self):
        return '<Author {}>'.format(self.as_dict())

    def as_dict(self):
        return {
            'id': self.id,
            'subscribers': self.subscribers,
            'email_subscribers': self.email_subscribers,
            'total_revenue': self.total_revenue,
            'monthly_fee': self.monthly_fee
        }


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    views = db.Column(db.Integer)
    original_post = db.Column(db.Text)
    post_edits = db.Column(ARRAY(db.String), default=[])
    free = db.Column(db.Boolean, default=False)
    revenue = db.Column(db.Integer, default=0)  # algorithm for percentage paid
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, onupdate=DateTime)

    def __repr__(self):
        return '<Post {}>'.format(self.as_dict())

    def as_dict(self):
        return {
            'id': self.id,
            'views': self.views,
            'original_post': self.original_post,
            'post_edits': self.post_edits,
            'free': self.free,
            'revenue': self.revenue,
            'author_id': self.author_id
        }


class UserBet(db.Model):
    __tablename__ = 'user_bets'

    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String)
    american_odds = db.Column(db.Integer)
    decimal_odds = db.Column(db.Numeric(10, 2))
    stake = db.Column(db.Numeric(10, 2))
    sportsbook = db.Column(db.String(50))
    handicap = db.Column(db.Numeric(10, 2), default=0)
    notification_handicap = db.Column(db.Numeric(10, 2), default=0)
    notification_price = db.Column(db.Numeric(10, 2), default=0)
    notification_completed = db.Column(db.Boolean, default=False)
    closing_line_value = db.Column(db.Numeric(10, 2), default=0)
    roi = db.Column(db.Numeric(10, 2), default=0)
    result = db.Column(ENUM(ResultsEnum))
    payout = db.Column(db.Numeric(10, 2))
    game_date = db.Column(db.DateTime)
    bet_date = db.Column(db.DateTime)
    active_wager = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    game_id = db.Column(db.Integer)
    league = db.Column(db.String)
    bet_type = db.Column(db.String)
    bet_for = db.Column(db.Boolean, default=True)
    odd_type = db.Column(ENUM(OddsTypeEnum))
    player_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)

    # def __repr__(self):
    #     return '<UserBet {}>'.format(self.as_dict())

    def as_dict(self):
        return {
            'id': self.id,
            'event': self.event,
            'american_odds': self.american_odds,
            'decimal_odds': float(self.decimal_odds) if self.decimal_odds else None,
            'stake': float(self.stake) if self.stake else None,
            'sportsbook': self.sportsbook,
            'handicap': float(self.handicap) if self.handicap else None,
            'notification_handicap': float(self.notification_handicap) if self.notification_handicap else None,
            'notification_price': float(self.notification_price) if self.notification_price else None,
            'notification_completed': self.notification_completed,
            'closing_line_value': float(self.closing_line_value) if self.closing_line_value else None,
            'return_on_investment': float(self.roi) if self.roi else None,
            'result': self.result.value if self.result else None,
            'payout': float(self.payout) if self.payout else None,
            'game_date': int(datetime.timestamp(self.game_date)) if self.game_date else None,
            'bet_date': int(datetime.timestamp(self.bet_date)) if self.bet_date else None,
            'active_wager': self.active_wager,
            'user_id': self.user_id,
            'game_id': self.game_id,
            'league': self.league,
            'bet_type': self.bet_type,
            'odd_type': self.odd_type.value,
            'player_id': self.player_id,
            'team_id': self.team_id,
            'bet_for': self.bet_for
        }


class Article(db.Model):
    __tablename__ = 'articles'

    article_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    headline = db.Column(db.String)
    source = db.Column(db.String)
    summary = db.Column(db.String)
    tags = db.Column(ARRAY(db.String), default=[])
    timestamp = db.Column(db.DateTime)
    url = db.Column(db.String)

    def as_dict(self):
        return {
            'article_id': self.article_id,
            'headline': self.headline,
            'source': self.source,
            'summary': self.summary,
            'tags': self.tags,
            'timestamp': int(datetime.timestamp(self.timestamp)),
            'url': self.url
        }

class Favourite_games(db.Model):
    __tablename__ = 'favourite_games'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, nullable=False)
    game_date = db.Column(db.DateTime, nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'game_id': self.game_id,
            'game_date': int(datetime.timestamp(self.game_date)) if self.game_date else None
        }

class Affiliates(db.Model):
    __tablename__ = 'affiliates'

    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String, nullable=False)
    region = db.Column(db.String, nullable=True)
    link = db.Column(db.String, nullable=False)
    provider = db.Column(db.String, nullable=True)
    
    def as_dict(self):
        return {
            'id': self.id,
            'book': self.book,
            'region': self.region,
            'link': self.link,
            'provider': self.provider
        }
