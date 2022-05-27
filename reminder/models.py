from datetime import datetime, date
from flask_login import UserMixin
from . import db
import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'User'
    __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    saved_for_notification = db.relationship(
        'Saved',
        foreign_keys='Saved.user_id',
        backref='User', lazy='dynamic')

    def get_id(self):
        return self.user_id

    def has_saved_title(self, tmdb_id):
        return db.session.query(Saved).filter_by(user_id=self.user_id,
                                                 tmdb_id=tmdb_id).count() > 0

    def save_title(self, tmdb_id, full_title_data):
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
                    air_date = datetime.datetime.strptime(air_date, '%Y-%m-%d').date()
                    notification = Notification(date=air_date, user_id=self.user_id, tmdb_id=title.tmdb_id)
                    db.session.add(notification)

        db.session.commit()

    def delete_title(self, tmdb_id):
        if self.has_saved_title(tmdb_id):
            db.session.query(Saved).filter_by(user_id=self.user_id,
                                              tmdb_id=tmdb_id).delete()

            db.session.query(Notification).filter_by(user_id=self.user_id,
                                                     tmdb_id=tmdb_id).delete()

            db.session.commit()


            # if other users aren't subscribed to this title notifications, we delete it completely
            # if not db.session.query(Saved).filter_by(tmdb_id=tmdb_id).count() > 0:
            #     db.session.query(Title).filter_by(tmdb_id=tmdb_id).delete()


class Title(db.Model):
    __tablename__ = 'Title'
    title_id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer)
    poster_path = db.Column(db.Text)
    name = db.Column(db.Text)
    year = db.Column(db.Integer)
    overview = db.Column(db.Text)
    in_production = db.Column(db.Boolean)
    air_dates = db.Column(db.Text)
    saves = db.relationship('Saved', backref='Title', lazy='dynamic')


class Saved(db.Model):
    __tablename__ = 'Saved'
    save_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    tmdb_id = db.Column(db.Integer, db.ForeignKey('Title.tmdb_id'))


class Notification(db.Model):
    __tablename__ = 'Notification'
    event_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    tmdb_id = db.Column(db.Integer, db.ForeignKey('Title.tmdb_id'))
