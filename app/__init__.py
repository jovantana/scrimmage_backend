import os
from flask import Flask, request
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from flask_cors import cross_origin, CORS
from .config import Config, rd, bcrypt, socketio, SCHEDULE_JOBS
from .home import home
from .user import login, sign_up, profile
from .content_blog.author import (
    author_dashboard, author_login, author_signup, create_post
)
from .content_blog import main_page, post_view
from .news import newsfeed, feedbin
from .betting import bet_slip, tracker, notifications
from .betting.metabet import (
    odds, scores, side_odds, odds_timer
)
from .models import db
from flask_apscheduler import APScheduler
from .user import profile


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    scheduler = APScheduler()
    
    if SCHEDULE_JOBS:
        print("SCHEDULE JOBS")
        
        scheduler.add_job(
            id="Update Odds Task", 
            func=odds_timer.update_odds,
            args=[app, db],
            trigger='interval', 
            seconds=60
        )

        scheduler.add_job(
            id="Erase inactive games Task", 
            func=odds_timer.delete_inactive_games,
            trigger='interval', 
            days=1
        )
        
        scheduler.add_job(
            id="Update Side Odds Task", 
            func=odds_timer.update_side_odds,
            trigger='interval', 
            seconds=300
        )
        
        scheduler.add_job(
            id="Check notifications", 
            func=notifications.check_updates,
            args=[app, db],
            trigger='interval', 
            seconds=20
        )
        
        scheduler.add_job(
            id="Check if games where finished and update UserBet", 
            func=notifications.check_game_over,
            args=[app, db],
            trigger='interval', 
            seconds=20
        )

        scheduler.add_job(
            id="Update newsfeed articles", 
            func=feedbin.get_feedbin_entries,
            args=[app, db],
            trigger='interval', 
            seconds=60
        )

        scheduler.add_job(
            id="Delete old newsfeed articles", 
            func=feedbin.delete_old_articles,
            args=[app, db],
            trigger='interval',
            days=1
        )
        
        scheduler.add_job(
            id="Delete old favourite games", 
            func=profile.delete_old_favourite_games,
            args=[app, db],
            trigger='interval',
            days=1
        )
    
    # SIDE ODDS once in 5 mins
    
    scheduler.start()

    app.register_blueprint(home.home_bp)
    app.register_blueprint(login.login_bp)
    app.register_blueprint(sign_up.signup_bp)
    app.register_blueprint(profile.profile_bp)
    app.register_blueprint(author_dashboard.auth_dash_bp)
    app.register_blueprint(author_login.author_login_bp)
    app.register_blueprint(author_signup.author_signup_bp)
    app.register_blueprint(create_post.create_post_bp)
    app.register_blueprint(bet_slip.bet_slip_bp)
    app.register_blueprint(tracker.tracker_bp)
    app.register_blueprint(newsfeed.newsfeed_bp)
    app.register_blueprint(main_page.main_content_page_bp)
    app.register_blueprint(post_view.post_view_bp)
    app.register_blueprint(odds.odds_bp)
    app.register_blueprint(scores.scores_bp)
    app.register_blueprint(side_odds.side_odds_bp)

    socketio.init_app(app, message_queue=os.environ.get('REDIS_URL'))
    rd.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)    

    return app
