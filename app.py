#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import PrimaryKeyConstraint, except_all
from forms import *
from flask_migrate import Migrate
from config import csrf
from wtforms.csrf.core import CSRF
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Dam1l0laak1nd3@localhost:5432/fyyur_main'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


moment = Moment(app)
app.config.from_object('config')


db = SQLAlchemy(app)
db.init_app(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(300), nullable=False)
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue', lazy=False)

    def __repr__(self):
        return f'<venue: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, twitter_link: {self.twitter_link}, instagram_link: {self.instagram_link}, brief_description: {self.brief_description}, website: {self.website}, Shows: {self.Shows}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String)
    seeking_venue = db.Column(db.String)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy=False)

    def __repr__(self):
        return f'<artist: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, spotify_link: {self.spotify_link}, instagram_link: {self.instagram_link}, twitter_link: {self.twitter_link}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        "artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)

    def __repr__(self):
        return f'<Show {self.id}, start_time: {self.start_time}, artist_id: {self.artist_id}, venue_id: {self.venue_id}>'


db.create_all()

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    # try:
    all_venues = Venue.query.order_by('city', 'state', 'name').all()

    data = []
    for v in all_venues:
        list_venues = []
        list_venues.append({
            'id': v.id,
            'name': v.name,
        })

        data.append({
            'city': v.city,
            'state': v.state,
            'venues': list_venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    term = request.form.get('search_term')
    searchFound = db.session.query(Venue).with_entities(
        Venue.id, Venue.name).filter(Venue.name.ilike('%' '%' + term + '%')).all()
    # if searchFound is not None:
    terms = []
    for found in searchFound:
        terms.append({
            'id': found.id,
            'name': found.name
        })
    response = {
        'count': len(searchFound),
        'data': terms
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = Venue.query.get(venue_id)

    upcoming_shows = []
    past_shows = []
    for S in data.shows:
        if S.start_time > datetime.now():
            upcoming_shows.append(S)
        else:
            past_shows.append(S)

    data.new_shows = upcoming_shows
    data.past_shows = past_shows

    return render_template('pages/show_venue.html', venue=data,)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    add_venue = Venue()
    error = False

    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        facebook_link = request.form['facebook_link']
        image_link = request.form['image_link']
        website_link = request.form['website_link']
        seeking_talent = request.form['seeking_talent']
        seeking_description = request.form['seeking_description']

        add_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link,
                          image_link=image_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)

        db.session.add(add_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')
    # TODO: modify data to be the data object returned from db insertion

    # TODO: on unsuccessful db insert, flash an error instead.


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        delete_venue = Venue.query.get(venue_id)
        venue_delete = delete_venue.name

        db.session.delete(delete_venue)
        db.session.comit()
        flash('Venue ' + venue_delete + ' successfully deleted.')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('Venue ' + venue_delete + ' could not be deleted')

    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    try:
        data = Artist.query.order_by('name').all()
    except Exception as error:
        data = None
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    term = request.form.get('search_term')
    searchFound = db.session.query(Artist).with_entities(
        Artist.id, Artist.name).filter(Artist.name.ilike('%' '%' + term + '%')).all()
    # if searchFound is not None:
    terms = []
    for found in searchFound:
        terms.append({
            'id': found.id,
            'name': found.name
        })
    response = {
        'count': len(searchFound),
        'data': terms
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    av_artist = db.session.query(Artist).get(artist_id)

    if not av_artist:
        flash('An error occurred')
        return render_template('/artists.html')

    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    upcoming_shows = []
    past_shows = []

    for S in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": S.venue_id,
            "venue_name": S.venue.name,
            "artist_image_link": S.venue.image_link,
            "start_time": S.start_time.strftime('%d-%m-%Y %H:%M:%S')
        })

    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
    past_shows = []

    for S in past_shows_query:
        past_shows.append({
            "venue_id": S.venue_id,
            "venue_name": S.venue.name,
            "artist_image_link": S.venue.image_link,
            "start_time": S.start_time.strftime('%d-%m-%Y %H:%M:%S')
        })

    data = {
        "id": av_artist.id,
        "name": av_artist.name,
        "genres": av_artist.genres,
        "city": av_artist.city,
        "state": av_artist.state,
        "phone": av_artist.phone,
        "website": av_artist.website_link,
        "facebook_link": av_artist.facebook_link,
        "seeking_venue": av_artist.seeking_venue,
        "seeking_description": av_artist.seeking_description,
        "image_link": av_artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    # TODO: populate form with fields from artist with ID <artist_id>
    form = ArtistForm(
        name=artist.name,
        city=artist.city,
        state=artist.state,
        phone=artist.phone,
        facebook_link=artist.facebook_link,
        genres=artist.genres,
        website_link=artist.website_link,
        image_link=artist.image_link,
        seeking_venue=artist.seeking_venue,
        seeking_description=artist.seeking_description)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.filter_by(id=artist_id).first()
    try:
        artist.name = request.form['name'],
        artist.city = request.form['city'],
        artist.state = request.form['state'],
        artist.phone = request.form['phone'],
        artist.facebook_link = request.form['facebook_link'],
        artist.website_link = request.form['website_link'],
        artist.image_link = request.form['image_link'],
        artist.genres = request.form['genres'],
        artist.seeking_venue = request.form['seeking_venue'],
        artist.seeking_description = request.form['seeking_description'],

        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception as eror:
        db.session.rollback()
        flash('Artist' + request.form['name'] + ' was not updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()

    form = VenueForm(
        name=venue.name,
        city=venue.city,
        state=venue.state,
        phone=venue.phone,
        address=venue.address,
        facebook_link=venue.facebook_link,
        genres=venue.genres,
        website_link=venue.website_link,
        image_link=venue.image_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description)

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue = Venue.query.filter_by(id=venue_id).first()
    # TODO: take values from the form submitted, and update existing

    try:
        venue.name = request.form['name'],
        venue.city = request.form['city'],
        venue.state = request.form['state'],
        venue.address = request.form['address'],
        venue.phone = request.form['phone'],
        venue.facebook_link = request.form['facebook_link'],
        venue.website_link = request.form['website_link'],
        venue.image_link = request.form['image_link'],
        venue.genres = request.form['genres'],
        venue.seeking_talent = request.form['seeking_talent'],
        venue.seeking_description = request.form['seeking_description'],

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except Exception as eror:
        db.session.rollback()
        flash('Venue ' + request.form['name'] + ' could not be updated!')

    finally:
        db.session.close()

    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    form = ArtistForm()
    add_artist = Artist()

    error = False

    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        facebook_link = request.form['facebook_link']
        image_link = request.form['image_link']
        website_link = request.form['website_link']
        seeking_venue = request.form['seeking_venue']
        seeking_description = request.form['seeking_description']

        add_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,
                            image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)

        # TODO: modify data to be the data object returned from db insertion
        db.session.add(add_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.all()
    data = []

    for S in shows:
        data.append({
            'venue_id': S.venue_id,
            'venue_name': S.venue.name,
            'artist_id': S.artist_id,
            'artist_name': S.artist.name,
            'image_link': S.artist.image_link,
            'start_time': S.start_time
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm()
    add_show = Show()
    error = False

    try:
        start_time = request.form['start_time']
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']

        add_show = Show(start_time=start_time,
                        artist_id=artist_id, venue_id=venue_id)

        # on successful db insert, flash success
        db.session.add(add_show)
        db.session.commit()
        flash('Show with artist id' +
              request.form['artist_id'] + ' was successfully listed!')
    except Exception as eror:
        # error = True
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show with artist id' +
              request.form['artist_id'] + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
