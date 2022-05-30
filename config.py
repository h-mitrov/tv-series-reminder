import os

API_KEY = os.environ.get('API_KEY')
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_USE_TLS = False                     # False for 465 port
MAIL_USE_SSL = True                      # True for 465 port
