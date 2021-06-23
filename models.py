
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()




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


    def create(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()



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

    def create(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
    




# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column( db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column( db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.datetime, nullable=False )
    
    def create(self):
        db.session.add(self)
        db.session.commit()
 
  