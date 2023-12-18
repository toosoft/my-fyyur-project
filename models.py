from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    website_link = db.Column(db.String(120))
    #genres = db.Column(db.ARRAY(db.String), nullable=False)  # genres = db.Column(ARRAY(String))
    #genres = db.Column(db.PickleType(mutable=True), nullable=False)  # genres = db.Column(ARRAY(String))
    genres = db.Column(db.PickleType, nullable=False)  # genres = db.Column(ARRAY(String))
    new_venue_time = db.Column(db.DateTime, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), nullable=False)
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.PickleType, nullable=False)  # genres = db.Column(ARRAY(String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default=' ')
    website_link = db.Column(db.String(120))
    new_artist_time = db.Column(db.DateTime, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), nullable=False)
    shows = db.relationship('Show', backref='Artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.String(), nullable=False)

# DONE: implement any missing fields, as a database migration using Flask-Migrate
