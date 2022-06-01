# Standard library imports
from datetime import datetime, date

# Third party imports
from flask_login import UserMixin

# Local application imports
from . import db


class User(db.Model, UserMixin):
    """
    User class. Works as a model for the database.
    """
    __tablename__ = 'User'
    __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def get_id(self) -> int:
        """
        Returns user id.
        """
        return self.user_id

    def has_saved_title(self, tmdb_id: int) -> bool:
        """
        Takes an int value as an argument, returns True if there is a saved title
        with such id in the 'Saved' table for current user.
        """
        return db.session.query(Saved).filter_by(user_id=self.user_id,
                                                 tmdb_id=tmdb_id).count() > 0

    def save_title(self, tmdb_id: int, full_title_data: dict) -> None:
        """
        Takes title id (int) and dictionary with full title data (name, air_dates,
        poster path, etc.). If the title wasn't previously saved by anyone, creates a new
        entry to the 'Title' table. After that, saves title to 'Saved' table for the current user.
        """
        title = db.session.query(Title).filter_by(tmdb_id=tmdb_id).first()

        if not title:
            title = Title(tmdb_id=full_title_data.get('tmdb_id'),
                          poster_path=full_title_data.get('poster_path'),
                          name=full_title_data.get('name'),
                          year=full_title_data.get('year'),
                          overview=full_title_data.get('overview'),
                          in_production=False if full_title_data.get('in_production') == 'False' else True,
                          air_dates=full_title_data.get('air_dates')
                          )
            db.session.add(title)

        if not self.has_saved_title(title.tmdb_id):
            saving = Saved(user_id=self.user_id, tmdb_id=title.tmdb_id)
            db.session.add(saving)
            if title.air_dates != 'None':
                for air_date in title.air_dates.split('|'):
                    air_date = datetime.strptime(air_date, '%Y-%m-%d').date()
                    notification = Notification(date=air_date, user_id=self.user_id, tmdb_id=title.tmdb_id)
                    db.session.add(notification)

        db.session.commit()

    def delete_title(self, tmdb_id: int) -> None:
        """
        Deletes title from 'Saved' table for the current user.
        Savings of the same title, performed by other users, stay unaffected.
        """
        if self.has_saved_title(tmdb_id):
            db.session.query(Saved).filter_by(user_id=self.user_id,
                                              tmdb_id=tmdb_id).delete()

            db.session.query(Notification).filter_by(user_id=self.user_id,
                                                     tmdb_id=tmdb_id).delete()

            db.session.commit()


class Title(db.Model):
    """
    Class Title. Works as a model for the database.
    """
    __tablename__ = 'Title'
    title_id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer)
    poster_path = db.Column(db.Text)
    name = db.Column(db.Text)
    year = db.Column(db.Text)
    overview = db.Column(db.Text)
    in_production = db.Column(db.Boolean)
    air_dates = db.Column(db.Text)
    
    def convert_to_dict(self) -> dict:
        """
        Represents all the current object data as a dictionary.
        """
        title_dict = dict()
        title_dict['tmdb_id'] = self.tmdb_id
        title_dict['poster_path'] = self.poster_path
        title_dict['name'] = self.name
        title_dict['year'] = self.year
        title_dict['overview'] = self.overview
        title_dict['in_production'] = self.in_production
        title_dict['air_dates'] = self.air_dates
        return title_dict


class Saved(db.Model):
    """
    Class Saved. Works as a model for the database.
    """
    __tablename__ = 'Saved'
    save_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    tmdb_id = db.Column(db.Integer)


class Notification(db.Model):
    """
    Class Notification. Works as a model for the database.
    """
    __tablename__ = 'Notification'
    event_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer)
    tmdb_id = db.Column(db.Integer)
