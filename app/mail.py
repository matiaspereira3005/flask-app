from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, current_app
)
from app.db import get_db

from mailjet_rest import Client

import os


bp = Blueprint('mail', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def index():
    search = request.args.get('search')
    db, c = get_db()

    if search is None:
        c.execute("SELECT * FROM email")
    else:
        c.execute("SELECT * FROM email WHERE content LIKE %s", ('%' + search + '%',))
    mails = c.fetchall()

    print(mails)
    return render_template('mails/index.html', mails=mails)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form.get('email')
        subject = request.form.get('subject')
        content = request.form.get('content')
        errors = []

        if not email:
            errors.append('Email es obligatorio')
        if not subject:
            errors.append('Asunto es obligatorio')
        if not content:
            errors.append('Contenido es obligatorio')

        if len(errors) == 0:
            send(email, subject, content)
            db, c = get_db()
            c.execute("INSERT INTO email (email, subject, content) VALUES (%s, %s, %s)",
                      (email, subject, content))
            db.commit()

            return redirect(url_for('mail.index'))
        else:
            for error in errors:
                flash(error)

    return render_template('mails/create.html')


def send(to, subject, content):
    mailjet = Client(auth=(
        current_app.config['MAILJET_KEY'], current_app.config['SECRET_KEY']), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": current_app.config['FROM_EMAIL']
                },
                "To": [
                    {
                        "Email": to
                    }
                ],
                "Subject": subject,
                "TextPart": content,
                # "HTMLPart": "<h3>Dear passenger 1, welcome to <a href='https://www.mailjet.com/'>Mailjet</a>!</h3><br />May the delivery force be with you!",
                "CustomID": "AppGettingStartedTest"
            }
        ]
    }
    result = mailjet.send.create(data=data)

    print(result.status_code)
    print(result.json())
