import click
from flask.cli import with_appcontext

from reminder import db
from . import models


# this is a command that creates the database tables. Has to be called from CLI on Heroku app settings
@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()
