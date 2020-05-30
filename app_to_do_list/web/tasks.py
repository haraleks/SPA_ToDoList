# from __future__ import absolute_import, unicode_literals

from flask_mail import Message
from settings import mail, app, celery


@celery.task
def send_async_email(email_data):

    """Background task to send an email with Flask-Mail."""
    with app.app_context():
        msg = Message(email_data['subject'],
                      sender=app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[email_data['to']])
        msg.body = email_data['body']
        mail.send(msg)
