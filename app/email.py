from threading import Thread
from flask import current_app, render_template, flash
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, template, subject, **kwargs):
    app = current_app._get_current_object()
    # mail.init_app(app)
    flash(app.config['MAIL_SERVER'])
    msg = Message(subject,
                  sender="chenjinbin11@sina.com", recipients=[to])
    # msg.body = "This is a first email"
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
