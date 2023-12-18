# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
# from datetime import datetime
# default = datetime.today()
# current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
from forms import *
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:12123@127.0.0.1:5432/postgres'
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
from models import *


# DONE: implement any missing fields, as a database migration using Flask-Migrate
# DONE: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    data1 = [
        {
            "time": v.new_venue_time,
            "state": v.state,
            "venues": [{
                "id": v.id,
                "name": v.name,
            }]
        } for v in session.query(Venue).order_by(Venue.new_venue_time.desc()).limit(10)   # session.query(Venue).distinct(Venue.state)
    ]
    data2 = [
        {
            "time": v.new_artist_time,
            "state": v.state,
            "venues": [{
                "id": v.id,
                "name": v.name,
            }]
        } for v in session.query(Artist).order_by(Artist.new_artist_time.desc()).limit(10)
    ]
    return render_template('pages/home.html', areas1=data1, areas2=data2)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    # -------- query db
    # venn = session.query(Venue)
    # OR_venn = Venue.query.all()
    # ven = session.query(Venue).filter(Venue.state == 'CA') -------get data by filtering
    # vena = session.query(Venue).filter(Venue.state.contains('CA'))
    # vena = session.query(Venue).filter(Venue.state.ilike('ca'))

    # -----------fetch data from database
    db_data = [
        {
            "city": v.city,
            "state": v.state,
            "venues": [{
                "id": V_s.id,
                "name": V_s.name,
                # "num_upcoming_shows": 0,
            } for V_s in session.query(Venue).filter(Venue.state == v.state)]
        } for v in session.query(Venue).distinct(Venue.state)
    ]

    return render_template('pages/venues.html', areas=db_data)


# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    if request.method == "POST":
        sc = request.form.get('search_category')
        ven_dot_category = getattr(Venue, sc)  # see setattr
        search_term = request.form.get('search_term', '')
        search = session.query(Venue).filter(ven_dot_category.ilike('%' + search_term + '%'))
        # ven_dot_category/attribute ::: Venue.name or Venue.city or Venue.state
        count = len(list(search))

        response = {
            "count": count,
            "data": [{
                "id": res.id,
                "name": res.name,
                # "num_upcoming_shows": 0,
            } for res in search]
        }

        return render_template('pages/search_venues.html', results=response, search_term=search_term, sc=sc)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    past_show = session.query(Show).filter(Show.start_time <= datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           Show.venue_id == venue_id)
    up_show = session.query(Show).filter(Show.start_time > datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                         Show.venue_id == venue_id)
    fetch_venue = session.query(Venue)

    # TODO: replace with real venue data from the venues table, using venue_id
    data1 = [{
        "id": v.id,
        "name": v.name,
        "genres": v.genres,  #v.genres.split(","),   split string into list, opp is seperator.join(list)
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website_link,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link,
        "past_shows": [{
            "artist_id": ps.artist_id,
            "artist_name": session.query(Artist).filter(Artist.id == ps.artist_id).first().name,
            "artist_image_link": session.query(Artist).filter(Artist.id == ps.artist_id).first().image_link,
            "start_time": ps.start_time
        } for ps in past_show],
        "upcoming_shows": [{
            "artist_id": up.artist_id,
            "artist_name": session.query(Artist).filter(Artist.id == up.artist_id).first().name,
            "artist_image_link": session.query(Artist).filter(Artist.id == up.artist_id).first().image_link,
            "start_time": up.start_time
        } for up in up_show],
        "past_shows_count": len(list(past_show)),
        "upcoming_shows_count": len(list(up_show)),
    } for v in fetch_venue]

    data = list(filter(lambda d: d['id'] == venue_id, data1))[0]
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------
# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    if request.method == 'POST':
        new_venue = dict(request.form)
        new_venue.update({"genres": request.form.getlist('genres')})
        new_venue.update({"seeking_talent": True})
        ven = Venue(**new_venue)

        try:
            session.add(ven)
            session.commit()
        except:
            session.rollback()
            # DONE: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            return redirect(url_for('index'))
        else:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('index'))

    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    fetch_venue = session.query(Venue).filter(Venue.id == venue_id).first()
    form = VenueForm()
    form.state.default = fetch_venue.state
    form.genres.default = fetch_venue.genres  #['Blues', 'Classical']  # fetch_venue.genres.split(",")
    form.process()

    venue = {
        "id": venue_id,
        "name": fetch_venue.name,
        "genres": fetch_venue.genres,
        "address": fetch_venue.address,
        "city": fetch_venue.city,
        "state": fetch_venue.state,
        "phone": fetch_venue.phone,
        "website": fetch_venue.website_link,
        "facebook_link": fetch_venue.facebook_link,
        "seeking_talent": fetch_venue.seeking_talent,
        "seeking_description": fetch_venue.seeking_description,
        "image_link": fetch_venue.image_link
    }
    # DONE: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


# DONE: take values from the form submitted, and update existing
#     venue record with ID <venue_id> using the new attributes
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    if request.method == 'POST':
        # new_venue = request.form
        new_venue = dict(request.form)
        new_venue.update({"genres": request.form.getlist('genres')})
        new_venue.update({"seeking_talent": False})

        # ven = Venue(**new_venue) #--------converts dictionary to class instance
        session.query(Venue).filter(Venue.id == venue_id).update(new_venue)
        session.commit()

    # on successful db insert, flash success
    flash('Venue, ' + request.form['name'] + ', was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))


# DONE: Complete this endpoint for taking a venue_id, and using
#     SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
#     BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
#     clicking that button deletes it from the db then redirect the user to the homepage
@app.route('/delete/<venue_id>')
def delete_venue(venue_id):
    try:
        session.query(Venue).filter(Venue.id == venue_id).delete()
        session.commit()
    except:
        session.rollback()
        flash("An Error occurred! No database entry deleted!")
        return redirect(url_for('venues'))
    else:
        flash('Venue with ID:' + venue_id + ' was DELETED successfully!')
        return redirect(url_for('index'))

    # return redirect(url_for('index', venue_id=venue_id))
    # return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    data = [{
        "id": ar.id,
        "name": ar.name,
    } for ar in session.query(Artist)]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    if request.method == "POST":

        sc = request.form.get('search_category')
        art_dot_category = getattr(Artist, sc)  # see setattr
        search_term = request.form.get('search_term', '')
        search = session.query(Artist).filter(art_dot_category.ilike('%' + search_term + '%'))
        count = len(list(search))

        response = {
            "count": count,
            "data": [{
                "id": res.id,
                "name": res.name,
                # "num_upcoming_shows": 0,
            } for res in search]
        }
        return render_template('pages/search_artists.html', results=response,
                               search_term=request.form.get('search_term', ''), sc=sc)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id

    past_show = session.query(Show).filter(Show.start_time <= datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           Show.artist_id == artist_id)
    up_show = session.query(Show).filter(Show.start_time > datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                         Show.artist_id == artist_id)

    fetch_artist = session.query(Artist)
    # DONE: replace with real artist data from the artist table, using artist_id
    data1 = [{
        "id": ar.id,
        "name": ar.name,
        "genres": ar.genres,
        "city": ar.city,
        "state": ar.state,
        "phone": ar.phone,
        "website": ar.website_link,
        "facebook_link": ar.facebook_link,
        "seeking_venue": ar.seeking_venue,
        "seeking_description": ar.seeking_description,
        "image_link": ar.image_link,
        "past_shows": [{
            "venue_id": ps.venue_id,
            "venue_name": session.query(Venue).filter(Venue.id == ps.venue_id).first().name,
            "venue_image_link": session.query(Venue).filter(Venue.id == ps.venue_id).first().image_link,
            "start_time": ps.start_time
        } for ps in past_show],
        "upcoming_shows": [{
            "venue_id": up.venue_id,
            "venue_name": session.query(Venue).filter(Venue.id == up.venue_id).first().name,
            "venue_image_link": session.query(Venue).filter(Venue.id == up.venue_id).first().image_link,
            "start_time": up.start_time
        } for up in up_show],
        "past_shows_count": len(list(past_show)),
        "upcoming_shows_count": len(list(up_show)),
    } for ar in fetch_artist]

    data = list(filter(lambda d: d['id'] == artist_id, data1))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    fetch_artist = session.query(Artist).filter(Artist.id == artist_id).first()

    form = ArtistForm()
    form.state.default = fetch_artist.state
    form.genres.default = fetch_artist.genres  # ['Blues', 'Classical']  # fetch_venue.genres.split(",")
    form.process()

    artist = {
        "id": artist_id,
        "name": fetch_artist.name,
        "genres": fetch_artist.genres,
        "city": fetch_artist.city,
        "state": fetch_artist.state,
        "phone": fetch_artist.phone,
        "website": fetch_artist.website_link,
        "facebook_link": fetch_artist.facebook_link,
        "seeking_venue": fetch_artist.seeking_venue,
        "seeking_description": fetch_artist.seeking_description,
        "image_link": fetch_artist.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    if request.method == 'POST':
        #new_artist = request.form
        new_artist = dict(request.form)
        new_artist.update({"genres": request.form.getlist('genres')})
        new_artist.update({"seeking_venue": False})
        flash(new_artist)
        # ven = Venue(**new_venue) #--------converts dictionary to class instance
        session.query(Artist).filter(Artist.id == artist_id).update(new_artist)
        session.commit()

    # on successful db insert, flash success
    flash('Artist, ' + request.form['name'] + ', was successfully updated!')

    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


# =======================================
# EDIT venue and submission was here
# ========================================


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    if request.method == 'POST':
        new_artist = dict(request.form)
        new_artist.update({"genres": request.form.getlist('genres')})
        new_artist.update({"seeking_venue": True})
        art = Artist(**new_artist)

        try:
            session.add(art)
            session.commit()
        except:
            session.rollback()
            # DONE: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            return redirect(url_for('index'))
        else:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('index'))
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [{
        "venue_id": sh.venue_id,
        "venue_name": session.query(Venue).filter(Venue.id == sh.venue_id).first().name,
        "artist_id": sh.artist_id,
        "artist_name": session.query(Artist).filter(Artist.id == sh.artist_id).first().name,
        "artist_image_link": session.query(Artist).filter(Artist.id == sh.artist_id).first().image_link,
        "start_time": sh.start_time,
    } for sh in session.query(Show)]

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    if request.method == 'POST':
        new_show = request.form
        sh = Show(**new_show)
        try:
            session.add(sh)
            session.commit()
        except:
            session.rollback()
            # DONE: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        else:
            # called to create new shows in the db, upon submitting new show listing form
            # DONE: insert form data as a new Show record in the db, instead
            # on successful db insert, flash success
            flash('Show was successfully listed!')
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
