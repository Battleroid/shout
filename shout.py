import os
from datetime import datetime, timedelta
from flask import Flask, url_for, redirect, render_template, session, flash
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form, RecaptchaField
from wtforms import StringField
from wtforms.validators import DataRequired, Length
import humanize

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

    def like(self):
        self.likes += 1

    def dislike(self):
        self.likes -= 1

    def __repr__(self):
        return '<Shout %r at %r>' % (self.shout, self.created)


@app.route('/add', methods=['POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        try:
            db.session.add(Shout(form.shout_text.data[:140]))
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
        flash('Shout added.')
    else:
        flash_errors(form)
    return redirect(url_for('index'))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash('Error in %s: %s' % (getattr(form, field).label.text, error))

@app.route('/like/<int:shout_id>', methods=['GET'])
def like(shout_id):
    target = Shout.query.get(shout_id)
    shout_id = str(shout_id)
    if not session.get(shout_id):
        set_vote_session(shout_id)
        target.like()
        db.session.commit()
        flash('Liked %s ...' % target.shout[:24])
    else:
        vote_time = session[shout_id] + timedelta(days=1)
        if vote_time > datetime.now():
            flash('You need to wait %s to vote on that again.' % humanize.naturaltime(vote_time))
        else:
            set_vote_session(shout_id)
            target.like()
            db.session.commit()
            flash('Liked %s ...' % target.shout[:24])
    return redirect(url_for('index'))


@app.route('/dislike/<int:shout_id>', methods=['GET'])
def dislike(shout_id):
    target = Shout.query.get(shout_id)
    shout_id = str(shout_id)
    if not session.get(shout_id):
        set_vote_session(shout_id)
        target.dislike()
        db.session.commit()
        flash('Disliked %s ...' % target.shout[:24])
    else:
        vote_time = session[shout_id] + timedelta(days=1)
        if vote_time > datetime.now():
            flash('You need to wait %s to vote on that again' % humanize.naturaltime(vote_time))
        else:
            set_vote_session(shout_id)
            target.dislike()
            db.session.commit()
            flash('Disliked %s ...' % target[:24])
    return redirect(url_for('index'))


def set_vote_session(shout_id_str):
    session[shout_id_str] = datetime.now()
    session.permanent = True


class AddForm(Form):
    shout_text = StringField('Shout', validators=[DataRequired(), Length(min=8, max=140)])
    recaptcha = RecaptchaField('ReCaptcha')


@app.route('/', methods=['GET'])
def index():
    form = AddForm()
    shouts = Shout.query.order_by(Shout.likes).limit(10).all()
    return render_template('index.html', title='Index', form=form, shouts=shouts)


if __name__ == '__main__':
    app.run(debug=True)