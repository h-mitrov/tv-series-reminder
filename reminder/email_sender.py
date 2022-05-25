from datetime import datetime, date
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


@email_sender.route("/send_notification")
def send_notification():
    current_date = date.today()

    # cleaning database from expired events : possibly, should create a separate function for this
    db.session.query(Notification).filter(Notification.date < current_date).delete()
    db.session.commit()

    # finding all notifications for today
    db.session.query(Notification).filter_by(date=current_date).all()

    # здесь нужно собрать очередь из писем - взять из полученных выше данных id сериала, просмотреть, кто его сохранил,
    # и тем отправить письма

    db.session.commit()

    return '<h1>Success</h1>'