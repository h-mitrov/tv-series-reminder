import click
from flask.cli import with_appcontext


# this is a command that creates the database tables. Has to be called from CLI on Heroku app settings
@click.command(name='create_tables')
@with_appcontext
def create_tables():
    from reminder import db, models
    db.create_all()
