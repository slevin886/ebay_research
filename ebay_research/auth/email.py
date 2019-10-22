from flask_mail import Message
from ebay_research import mail
from flask import render_template, current_app
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(user, subject, template):
    app = current_app._get_current_object()
    token = user.get_confirmation_token()
    msg = Message('[Genius Bidding]' + ' ' + subject,
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = render_template(template + '.txt', user=user, token=token)
    msg.html = render_template(template + '.html', user=user, token=token)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_comment(sender, subject, user_message):
    app = current_app._get_current_object()
    msg = Message('[Genius Bidding]' + ' ' + subject,
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[app.config['MAIL_DEFAULT_SENDER']])
    msg.body = render_template('email/send_comment.txt', sender=sender, user_message=user_message)
    msg.html = render_template('email/send_comment.html', sender=sender, user_message=user_message)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
