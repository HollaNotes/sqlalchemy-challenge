# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    year_from_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    precip_date_year_from_recent = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_from_recent).all()

    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()
    stations = list(np.ravel(stations))
    return jsonify(stations)

@app.route("/api/v1.0/tobs") 
def tobs():
    year_from_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station_tobs = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= year_from_recent).all()
    tobs = list(np.ravel(most_active_station_tobs))
    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def