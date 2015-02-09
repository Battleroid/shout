import os
from datetime import datetime
from flask import Flask, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form, RecaptchaField
from wtforms import StringField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
SECRET_KEY = os.urandom(64)
RECAPTCHA_PUBLIC_KEY = '6LfrqAETAAAAAO_BbffXgjLZJ_iEOHNgGBy5Jo2z'
RECAPTCHA_PRIVATE_KEY = '6LfrqAETAAAAABe7HiBUZAMy9M-lp7kunMwp42eB'
SQLALCHEMY_DATABASE_URI = 'mysql://shout:shout@127.0.0.1/shout'
app.config.from_object(__name__)
db = SQLAlchemy(app)


class Shout(db.Model):
    __tablename__ = 'shout'

    id = db.Column(db.Integer, primary_key=True)
    shout = db.Column(db.String(140), nullable=False)
    likes = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, shout):
        self.shout = shout

    def __repr__(self):
        return '<Shout %r at %r>' % (self.shout, self.created)


@app.route('/add', methods=['POST'])
def add():
    form = AddForm()
    if form.validate():
        print 'True'
    return redirect(url_for('index'))


class AddForm(Form):
    shout_text = StringField([DataRequired(), Length(140)])
    recaptcha = RecaptchaField()


@app.route('/', methods=['GET'])
def index():
    form = AddForm()
    return render_template('index.html', title='Index', form=form)


if __name__ == '__main__':
    app.run()
