# Third party imports
import click
from flask.cli import with_appcontext


# this is a command that creates the database tables. Has to be called from CLI on Heroku app settings
@click.command(name='create_tables')
@with_appcontext
def create_tables():
    """
    It is used to manually create or update the database with a simple
    'flask create_tables' command in the terminal.
    """
    from reminder import db, models
    db.create_all()
