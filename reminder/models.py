from flask_login import UserMixin
from . import db


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

    def save_title(self, title):
        if not self.has_saved_title(title):
            saving = Saved(user_id=self.user_id, title_id=title.title_id)
            db.session.add(saving)

    def delete_title(self, title):
        if self.has_saved_title(title):
            Saved.query.filter_by(
                user_id=self.user_id,
                title_id=title.title_id).delete()

    def has_saved_title(self, title):
        return Saved.query.filter(
            Saved.user_id == self.user_id,
            Saved.title_id == title.title_id).count() > 0


class Saved(db.Model):
    __tablename__ = 'Saved'
    save_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    title_id = db.Column(db.Integer, db.ForeignKey('Title.title_id'))


class Title(db.Model):
    __tablename__ = 'Title'
    title_id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    saves = db.relationship('Saved', backref='Title', lazy='dynamic')
