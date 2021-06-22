#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String())
    num_upcoming_shows = db.Column(db.Integer, default=0)
    num_past_shows = db.Column(db.Integer, default=0)
    show = db.relationship('Show', backref='venue',
    cascade='delete,save-update',lazy=True)
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String())
    num_upcoming_shows = db.Column(db.Integer, default=0)
    num_past_shows = db.Column(db.Integer, default=0)
    show = db.relationship('Show', backref='artist',
    cascade='delete,save-update',lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column( db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column( db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.datetime, nullable=False )

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []
  # Get the venues after group it by state and city 
  venues = db.session.query(Venue.city,Venue.state).group_by(Venue.state,Venue.city).all()
  for venue in venues:
    num_upcoming_shows=0
    venues_data =[]
    # Get the venues of specific  state and city
    venues_list = Venue.query.filter(Venue.city == venue.city).filter( Venue.state == venue.state).all()
    # Get the number of shows for a vunue
    for venue in venues_list:
      upcoming_shows =Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.datetime.now()).all()
      for show in upcoming_shows:
        num_upcoming_shows += 1

      # Add the required info of venue to a list 
      venues_data.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': num_upcoming_shows
        })

    # Add the required info of venue to a list 
    data.append({
      'city': venue.city,
      'state': venue.state,
      'venues': venues_data
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  
  search_venues =[]
  num_upcoming_shows = 0
  count = 0
  
  # Get the entered word from search box
  search_term = request.form['search_term']
  search_data = Venue.query.filter(Venue.name.ilike( '%' + search_term + '%'))

  # Get the upcoming shows of a venue
  for search in search_data:
    upcoming_shows =Show.query.filter(Show.venue_id == search.id).filter(Show.start_time > datetime.datetime.now()).all()
    for show in upcoming_shows:
      num_upcoming_shows += 1
   # Add the required info of searched venue to a list 
    search_venues.append({
        'id': search.id,
        'name': search.name,
        'num_upcoming_shows':num_upcoming_shows
      })
  # Get the number of search results of a venue
  for search in search_data:
    count += 1 
  # Add the required info of searched venue to a list 
  response ={
   'count':count,
   'data': search_venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  past_shows_count = 0
  num_upcoming_shows = 0
  data =[]

  # Get venue data by the given id
  venue_list = Venue.query.get(venue_id)
  # Get upcoming shows of this venue
  upcoming_shows =Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.datetime.now()).all()
  # Get the number of upcoming shows of this venue
  for show in upcoming_shows:
   num_upcoming_shows += 1

  if num_upcoming_shows > 0:
    upcoming_shows_data = []

    # Get the upcoming shows of the artist in the venue if any
    for show in upcoming_shows:
      venue_show = Venue.query.filter(Venue.id == show.venue_id).first()
      # Add artist data to the list of upcoming shows
      upcoming_shows_data.append({
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': str(show.start_time)
      }) 
            
  # Get past shows of this venue
  past_shows =Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.datetime.now()).all()
  # Get the number of past shows of this venue
  for show in past_shows:
    past_shows_count += 1

  if past_shows_count > 0:
    past_shows_data = []

    # Get the past shows of the artist in the venue if any 
    for show in past_shows:
      venue = Venue.query.filter(Venue.id == show.venue_id).first()

      # Add artist data to the list of past shows
      past_shows_data.append({     
       'artist_id': show.artist.id,
       'artist_name': show.artist.name,
       'artist_image_link': show.artist.image_link,
       'start_time': str(show.start_time)
        })

 # I implement the next if-elif-else statements because I faced problem when adding 
 # new venue without upcoming and past shows or venue with past show only or 
 # upcoming show only...       

  if num_upcoming_shows == 0 and past_shows_count == 0:
   data ={
    "id": venue_list.id,
    "name": venue_list.name,
    "address": venue_list.address,
    "genres": venue_list.genres.split(','),
    "city": venue_list.city,
    "state": venue_list.state,
    "phone": venue_list.phone,
    "website_link": venue_list.website_link,
    "facebook_link": venue_list.facebook_link,
    "seeking_talent": venue_list.seeking_talent,
    "seeking_description": venue_list.seeking_description,
    "image_link": venue_list.image_link,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": num_upcoming_shows
   }
  elif num_upcoming_shows > 0 and past_shows_count == 0:
    data ={
    "id": venue_list.id,
    "name": venue_list.name,
    "address": venue_list.address,
    "genres": venue_list.genres.split(','),
    "city": venue_list.city,
    "state": venue_list.state,
    "phone": venue_list.phone,
    "website_link": venue_list.website_link,
    "facebook_link": venue_list.facebook_link,
    "seeking_talent": venue_list.seeking_talent,
    "seeking_description": venue_list.seeking_description,
    "image_link": venue_list.image_link,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": num_upcoming_shows
   }
  elif num_upcoming_shows == 0 and past_shows_count > 0:
    data ={
    "id": venue_list.id,
    "name": venue_list.name,
    "address": venue_list.address,
    "genres": venue_list.genres.split(','),
    "city": venue_list.city,
    "state": venue_list.state,
    "phone": venue_list.phone,
    "website_link": venue_list.website_link,
    "facebook_link": venue_list.facebook_link,
    "seeking_talent": venue_list.seeking_talent,
    "seeking_description": venue_list.seeking_description,
    "image_link": venue_list.image_link,
    "past_shows": past_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": num_upcoming_shows
   }
  else:
   data ={
    "id": venue_list.id,
    "name": venue_list.name,
    "address": venue_list.address,
    "genres": venue_list.genres.split(','),
    "city": venue_list.city,
    "state": venue_list.state,
    "phone": venue_list.phone,
    "website_link": venue_list.website_link,
    "facebook_link": venue_list.facebook_link,
    "seeking_talent": venue_list.seeking_talent,
    "seeking_description": venue_list.seeking_description,
    "image_link": venue_list.image_link,
    "past_shows": past_shows_data,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": num_upcoming_shows
   }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  # Get the required data to create a new venue from the form 
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website_link = request.form['website_link']
  seeking_talent = True if 'seeking_talent' in request.form else False
  seeking_description = request.form['seeking_description']
  # Add data to a venue model
  new_Venue = Venue(
    name=name,
    city=city,
    state=state,
    address=address,
    phone=phone,
    genres=genres,
    image_link=image_link,
    facebook_link=facebook_link,
    website_link=website_link,
    seeking_talent=seeking_talent,
    seeking_description=seeking_description,
  )
  # on successful db insert, flash success
  try:
    #Add the new venue to db
    db.session.add(new_Venue)
    db.session.commit()  
    flash('Venue ' + request.form['name'] + ' was added successfully!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred, Venue ' + request.form['name'] + ' could not be added.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close() 
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  #Get the venue by given id
 venue = Venue.query.filter_by(id=venue_id).first()
 try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash(venue.name + 'venue was deleted successfully!')
 except:
    db.session.rollback()
    flash(venue.name + "venue was n't deleted successfully!")
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

  data = []
  #Get the artists data
  artists_data =Artist.query.all()
  
  for artist in artists_data:
   #Add required artist data to a list
    data.append({
      'id':artist.id,
      'name': artist.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_artists =[]
  num_upcoming_shows = 0
  count = 0
  #Get the entered word from the search box
  search_term = request.form['search_term']
  search_data = Artist.query.filter(Artist.name.ilike( '%' + search_term + '%'))
  
  #Get upcoming shows of an artist
  for search in search_data:
    upcoming_shows =Show.query.filter(Show.artist_id == search.id).filter(Show.start_time > datetime.datetime.now()).all()
    for show in upcoming_shows:
      num_upcoming_shows += 1
    # Add the required info of searched artist to a list
    search_artists.append({
      'id': search.id,
      'name': search.name,
      'num_upcoming_shows':num_upcoming_shows
      })
   # Get the number of search results of an artist
  for search in search_data:
    count += 1 
  # Add the required info of searched artist to a list
  response ={
   'count':count,
   'data': search_artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  past_shows_count = 0
  num_upcoming_shows = 0
  data=[]
   # Get artist data by the given id
  artist_list = Artist.query.get(artist_id)
   # Get upcoming shows of this artist
  upcoming_shows =Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.datetime.now()).all()
   # Get the number of upcoming shows of this artist
  for show in upcoming_shows:
     num_upcoming_shows += 1

  if num_upcoming_shows > 0:
      upcoming_shows_data = []

      # Get the upcoming venue shows of the artist if any
      for show in upcoming_shows:
        venue_show = Venue.query.filter(Venue.id == show.venue_id).first()
        # Add venue data to the list of upcoming shows
        upcoming_shows_data.append({
          'venue_id': venue_show.id,
          'venue_name': venue_show.name,
          'venue_image_link': venue_show.image_link,
          'start_time': str(show.start_time),
        })

   # Get past shows of this artist
  past_shows =Show.query.filter(Show.artist_id == artist_id).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.datetime.now()).all()
  # Get the number of past shows of the artist
  for show in past_shows:
    past_shows_count += 1

  if past_shows_count > 0:
    past_shows_data = []

     # Get the past venue shows of the artist if any
    for show in past_shows:
        venue = Venue.query.filter(Venue.id == show.venue_id).first()
        # Add venue data to the list of past shows
        past_shows_data.append({
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': str(show.start_time),
        })
 # I implement the next if-elif-else statements because I faced problem when adding 
 # new artist without upcoming and past shows or artist with past show only or 
 # upcoming show only...  
  if num_upcoming_shows == 0 and past_shows_count == 0:
   data ={
    "id": artist_list.id,
    "name": artist_list.name,
    "genres": artist_list.genres.split(','),
    "city": artist_list.city,
    "state": artist_list.state,
    "phone": artist_list.phone,
    "website_link": artist_list.website_link,
    "facebook_link": artist_list.facebook_link,
    "seeking_venue": artist_list.seeking_venue,
    "seeking_description": artist_list.seeking_description,
    "image_link": artist_list.image_link,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": num_upcoming_shows
   }
  elif num_upcoming_shows > 0 and past_shows_count == 0:
   data ={
    "id": artist_list.id,
    "name": artist_list.name,
    "genres": artist_list.genres.split(','),
    "city": artist_list.city,
    "state": artist_list.state,
    "phone": artist_list.phone,
    "website_link": artist_list.website_link,
    "facebook_link": artist_list.facebook_link,
    "seeking_venue": artist_list.seeking_venue,
    "seeking_description": artist_list.seeking_description,
    "image_link": artist_list.image_link,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": num_upcoming_shows
   }
  elif num_upcoming_shows == 0 and past_shows_count > 0:
   data ={
    "id": artist_list.id,
    "name": artist_list.name,
    "genres": artist_list.genres.split(','),
    "city": artist_list.city,
    "state": artist_list.state,
    "phone": artist_list.phone,
    "website_link": artist_list.website_link,
    "facebook_link": artist_list.facebook_link,
    "seeking_venue": artist_list.seeking_venue,
    "seeking_description": artist_list.seeking_description,
    "image_link": artist_list.image_link,
    "past_shows": past_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": num_upcoming_shows
   }
  else:
    data ={
    "id": artist_list.id,
    "name": artist_list.name,
    "genres": artist_list.genres.split(','),
    "city": artist_list.city,
    "state": artist_list.state,
    "phone": artist_list.phone,
    "website_link": artist_list.website_link,
    "facebook_link": artist_list.facebook_link,
    "seeking_venue": artist_list.seeking_venue,
    "seeking_description": artist_list.seeking_description,
    "image_link": artist_list.image_link,
    "past_shows": past_shows_data,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": num_upcoming_shows
   }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
# Get the artist by the given id 
 artist = Artist.query.get(artist_id)
 # Fill artist data in the form 
 form = ArtistForm()
 form.name.data = artist.name
 form.city.data = artist.city
 form.state.data = artist.state
 form.phone.data = artist.phone
 form.genres.data = artist.genres
 form.facebook_link.data = artist.facebook_link
 form.image_link.data = artist.image_link
 form.website_link.data = artist.website_link
 form.seeking_venue.data = artist.seeking_venue
 form.seeking_description.data = artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
 return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  # Get the artist by the given id 
 artist = Artist.query.get(artist_id)
  #Update artist data
 try:
   artist.name = request.form['name']
   artist.city = request.form['city']
   artist.state = request.form['state']
   artist.phone = request.form['phone']
   artist.facebook_link = request.form['facebook_link']
   artist.website_link = request.form['website_link']
   artist.image_link = request.form['image_link']
   artist.genres = request.form.getlist('genres')
   artist.seeking_venue = True if 'seeking_venue' in request.form else False
   artist.seeking_description = request.form['seeking_description']
   db.session.commit()
   flash(" {} info was updated successfully!".format(artist.name))
 except:
    db.session.rollback()
    flash(" {} info wasn't updated successfully!".format(artist.name))
 finally:
    db.session.close()

 return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
 # Get the venue by the given id 
 venue = Venue.query.get(venue_id)
 # Fill venue data in the form
 form = VenueForm()
 form.name.data = venue.name
 form.city.data = venue.city
 form.state.data = venue.state
 form.address.data = venue.address
 form.phone.data = venue.phone
 form.image_link.data = venue.image_link
 form.genres.data = venue.genres
 form.facebook_link.data = venue.facebook_link
 form.website_link.data = venue.website_link
 form.seeking_talent.data = venue.seeking_talent
 form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
 return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  # Get the venue by the given id 
 venue = Venue.query.get(venue_id)
  #Update venue data
 try:
   venue.name = request.form['name']
   venue.city = request.form['city']
   venue.state = request.form['state']
   venue.address = request.form['address']
   venue.phone = request.form['phone']
   venue.image_link = request.form['image_link']
   venue.genres = request.form.getlist('genres')
   venue.facebook_link = request.form['facebook_link']
   venue.website_link = request.form['website_link']
   venue.seeking_talent = True if 'seeking_talent' in request.form else False
   venue.seeking_description = request.form['seeking_description']
   db.session.commit()
   flash(" {} info was updated successfully!".format(venue.name))
 except:
    db.session.rollback()
    flash(" {} info wasn't updated successfully!".format(venue.name))
 finally:
    db.session.close()
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
  # TODO: modify data to be the data object returned from db insertion

  # Get the required data to create a new artist 
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website_link = request.form['website_link']
  seeking_venue = True if 'seeking_venue' in request.form else False
  seeking_description = request.form['seeking_description']
  # Add data to artist model
  new_Artist = Artist(
    name=name,
    city=city,
    state=state,
    phone=phone,
    genres=genres,
    facebook_link=facebook_link,
    image_link=image_link,
    website_link=website_link,
    seeking_venue=seeking_venue,
    seeking_description=seeking_description,
  )
  # on successful db insert, flash success
  try:
    #Add the new artist to db
    db.session.add(new_Artist)
    db.session.commit()  
    flash('Artist' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close() 
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  data=[]
  # Get all shows data
  shows_data =Show.query.all()
  # Itrare on shows data to get info of shows  
  for show in shows_data:
  # Add required data to a list
    data.append({
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'start_time': str(show.start_time)
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
  
  # Get the required data to create new show from the form
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  # Add data to show model
  new_Show = Show(
   artist_id = artist_id,
   venue_id = venue_id,
   start_time = start_time
  )
  try:
   # Add the new show to db
   db.session.add(new_Show)
   db.session.commit()
   # on successful db insert, flash success
   flash('Show was successfully listed!')
  except:
    db.session.rollback()
   # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
