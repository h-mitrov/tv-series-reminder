from flask import Blueprint, render_template
from flask_mail import Mail, Message
from . import mail
from .models import Saved, User, Title


email_sender = Blueprint('email_sender', __name__)


@email_sender.route("/send_email")
def email():
    msg = Message('Hello!', sender='tvreminder@yahoo.com', recipients=['mitrovgn@gmail.com'])
    msg.body = 'hello'
    mail.send(msg)
    return 'email sent'


@email_sender.route("/send_notification")
def send_notification():



    messages_for_today = []


    msg = Message('Hello!', sender='tvreminder@yahoo.com', recipients=['mitrovgn@gmail.com'])
    msg.body = 'hello'
    mail.send(msg)
    return 'email sent'