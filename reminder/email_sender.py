# Standard library imports
from datetime import datetime, date
import time

# Third party imports
from flask import Blueprint, render_template
from flask_mail import Mail, Message

# Local application imports
from . import db, mail
from .models import Saved, User, Title, Notification


email_sender = Blueprint('email_sender', __name__)


@email_sender.route("/send_notifications")
def send_notifications() -> str:
    """ Sends email notifications to users. Takes no arguments. """

    current_date = date.today()
    messages_dict = dict()

    # cleaning database from expired events : possibly, should create a separate function for this
    db.session.query(Notification).filter(Notification.date < current_date).delete()
    db.session.commit()

    # finding all notifications for today and assigning them to a certain email
    relevant_notifications = db.session.query(Notification).filter_by(date=current_date).all()
    unique_users = set(notification.user_id for notification in relevant_notifications)

    # creating an email dictionary with all necessary info
    for i_user in unique_users:
        user = db.session.query(User).filter_by(user_id=i_user).first()
        todays_ids = [int(notification.tmdb_id) for notification in relevant_notifications if notification.user_id == i_user]
        titles = db.session.query(Title).filter(Title.tmdb_id.in_(todays_ids)).all()
        messages_dict[i_user] = [user.email, user.name, [title.name for title in titles]]

    # rendering and sending emails
    for i_user in messages_dict:
        user_email, user_name, user_titles = messages_dict[i_user]
        message = Message(subject='Reminder: new TV series episodes are here',
                          sender='tvreminder@yahoo.com',
                          recipients=[user_email])
        message.html = render_template('email_message.html', user_name=user_name, user_titles=user_titles)
        mail.send(message)
        time.sleep(3)

    return '<h1>Success</h1>', 200
