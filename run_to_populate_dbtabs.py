from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import psycopg2

# from gevent.pywsgi import WSGIServer
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:12123@127.0.0.1:5432/postgres'
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


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
    seeking_description = db.Column(db.String(500))
    seeking_talent = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
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
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    new_artist_time = db.Column(db.DateTime, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), nullable=False)
    shows = db.relationship('Show', backref='Artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.String(), nullable=False)


# ----insert app mock data into database

# ----insert app mock data into database
data1 = {
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website_link": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
}

ven1 = Venue(**data1)
# OR ven1 = Venue(name="The Musical Hop", genres="Jazz, Reggae, Swing, Classical, Folk", address="1015 Folsom Street",
# city="San Francisco", state="CA", phone="123-123-1234",\ website_link="https://www.themusicalhop.com",
# facebook_link="https://www.facebook.com/TheMusicalHop", seeking_talent="True",
# image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto
# =format&fit=crop&w=400&q=60",\ )

data2 = {
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website_link": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
}
ven2 = Venue(**data2)

data3 = {
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website_link": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
}
ven3 = Venue(**data3)

session.add_all([ven1, ven2, ven3])
session.commit()

data11 = {
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website_link": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
}
art11 = Artist(**data11)

data22 = {
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
}
art22 = Artist(**data22)

data33 = {
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
}
art33 = Artist(**data33)

session.add_all([art11, art22, art33])
session.commit()

data = [{
    "venue_id": 1,
    "artist_id": 4,
    "start_time": "2019-05-21T21:30:00.000Z"
}, {
    "venue_id": 3,
    "artist_id": 5,
    "start_time": "2019-06-15T23:00:00.000Z"
}, {
    "venue_id": 3,
    "artist_id": 6,
    "start_time": "2035-04-01T20:00:00.000Z"
}, {
    "venue_id": 3,
    "artist_id": 6,
    "start_time": "2035-04-08T20:00:00.000Z"
}, {
    "venue_id": 3,
    "artist_id": 6,
    "start_time": "2035-04-15T20:00:00.000Z"
}]

count = len(data)
# ----------------------------------------------------------------------------------------------------------------------
# get dict: data[0]; put the dict in Show object; repeat.. until count; put results inside list, [] assign to variable x
x = [Show(**data[i]) for i in range(count)]
# ----------------------------------------------------------------------------------------------------------------------
session.add_all(x)
session.commit()


# experiment ...... print([i for i in (for i in range(count))])
# experiment ...... session.add_all([Show(**data[i]) for i in (for i in range(count))])
# worked ..........print([Show(**data[i]) for i in range(count)])
# worked ..........session.add_all([Show(**data[i]) for i in range(count)])


