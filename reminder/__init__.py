from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import config


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# init Mail to use it in our Email Sender blueprint
mail = Mail()


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = 'kkskdfksjdfslkdj23'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    app.config.from_object(config)
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

    return app


