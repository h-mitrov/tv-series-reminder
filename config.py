# Standard library imports
import os


# Flask settings
FLASK_ENV = os.environ.get('FLASK_ENV')
SECRET_KEY = os.environ.get('SECRET_KEY')

# database settings
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# TMDB API settings
API_KEY = os.environ.get('API_KEY')

# email settings
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_USE_TLS = False                     # False for 465 port
MAIL_USE_SSL = True                      # True for 465 port
