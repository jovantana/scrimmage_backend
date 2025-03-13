import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_redis.client import FlaskRedis
from flask_socketio import SocketIO
import json

socketio = None

REGIONS = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
          "Canada", "Europe", "UK", "Africa", "South America", "Brazil",
          "Oceania", "Australia", "Asia", "Russia", "Antarctica", "Atlantis", "Other"]

if os.environ.get('FLASK_ENV') != 'development':
    print("ENABLE EVENTLER")
    import eventlet
    eventlet.monkey_patch()
    socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')
else:
    socketio = SocketIO(cors_allowed_origins="*", logger=True)

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

rd = FlaskRedis()
bcrypt = Bcrypt()

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    FEEDS_BASEURL = os.environ.get('FEEDS_BASEURL')
    FEEDS_USEAREMAIL = os.environ.get('FEEDS_USEAREMAIL')
    FEEDS_PASSWORD = os.environ.get('FEEDS_PASSWORD')
    FEEDS_KEYS = os.environ.get('FEEDS_KEYS')

SPORTSRADAR_KEY = os.environ.get('SPORTSRADAR_KEY')
META_KEY = os.environ.get('META_KEY')
SCHEDULE_JOBS = json.loads(os.environ.get('SCHEDULE_JOBS', 'true').lower())
print(str(os.environ))

TEAM_LOGOS = None

with open(os.path.join('app/betting/json_scripts', 'team_logos.json'), 'r') as file:
    TEAM_LOGOS = json.load(file)
