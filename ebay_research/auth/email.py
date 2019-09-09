from flask_mail import Message
from ebay_research import mail
from flask import render_template
import os


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_confirmation_email(user):
    token = user.get_confirmation_token()
    send_email('[Genius Bidding] Confirm Your Email',
               sender=os.environ.get('MAIL_DEFAULT_SENDER'),
               recipients=[user.email],
               text_body=render_template('email/confirm_email.txt', user=user, token=token),
               html_body=render_template('email/confirm_email.html', user=user, token=token)
               )
