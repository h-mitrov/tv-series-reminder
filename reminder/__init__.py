# Standard library imports
import os
import sys
import time
import atexit
import logging

# Third party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler

# Local application imports
import config
from .create_database import create_tables


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# init Mail to use it in our Email Sender blueprint
mail = Mail()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    mail.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, we use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for main app
    from . import reminder
    app.register_blueprint(reminder.main_app)

    # blueprint for auth routes
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for email sender
    from .email_sender import email_sender as email_blueprint
    app.register_blueprint(email_blueprint)

    # this condition prevents scheduler from running twice
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # init scheduler for everyday notification sending
        from .email_sender import send_notifications

        scheduler = BackgroundScheduler()
        scheduler.add_job(func=send_notifications, trigger="interval", days=1)
        scheduler.start()

        # shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

    # added database command for creating tables
    app.cli.add_command(create_tables)

    # added exceptions logger to see them in Heroku logs
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    return app


def get_app():
    app = create_app()
    return app

