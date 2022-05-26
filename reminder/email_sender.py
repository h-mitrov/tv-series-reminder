from datetime import datetime, date
import time
from flask import Blueprint, render_template
from flask_mail import Mail, Message
from . import db, mail
from .models import Saved, User, Title, Notification

email_sender = Blueprint('email_sender', __name__)


@email_sender.route("/send_email")
def email():
    msg = Message('Hello!', sender='tvreminder@yahoo.com', recipients=['mitrovgn@gmail.com'])
    msg.body = 'hello'
    mail.send(msg)
    return 'email sent'


@email_sender.route("/send_notifications")
def send_notifications():
    current_date = date.today()
    messages_dict = dict()

    # array = [103516, 11, 12]
    # titles = db.session.query(Title).filter(Title.tmdb_id.in_(array)).all()
    # result = ''
    # for title in titles:
    #     result += title.name


    # cleaning database from expired events : possibly, should create a separate function for this
    db.session.query(Notification).filter(Notification.date < current_date).delete()
    db.session.commit()

    # finding all notifications for today and assigning them to a certain email
    relevant_notifications = db.session.query(Notification).filter_by(date=current_date).all()
    unique_users = set([notification.user_id for notification in relevant_notifications])

    for i_user in unique_users:
        user = db.session.query(User).filter_by(user_id=i_user).first()
        todays_ids = [int(notification.tmdb_id) for notification in relevant_notifications if notification.user_id == i_user]
        titles = db.session.query(Title).filter(Title.tmdb_id.in_(todays_ids)).all()
        messages_dict[i_user] = [user.email, user.name, [title.name for title in titles]]

    for i_user in messages_dict:
        user_email, user_name, user_titles = messages_dict[i_user]
        message = Message(subject='Reminder: new TV series episodes are here',
                          sender='tvreminder@yahoo.com',
                          recipients=[user_email])
        message.html = render_template('email_message.html', user_name=user_name, user_titles=user_titles)
        mail.send(message)
        time.sleep(5)

    return '', 200
