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


# def send_email(subject, sender, recipients, text_body, html_body):
#     msg = Message(subject, sender=sender, recipients=recipients)
#     msg.body = text_body
#     msg.html = html_body
#     mail.send(msg)
#
#
# def send_confirmation_email(user, email_text, email_html):
#     token = user.get_confirmation_token()
#     send_email('[Genius Bidding] Confirm Your Email',
#                sender=os.environ.get('MAIL_DEFAULT_SENDER'),
#                recipients=[user.email],
#                text_body=render_template(email_text, user=user, token=token),
#                html_body=render_template(email_html, user=user, token=token)
#                )
