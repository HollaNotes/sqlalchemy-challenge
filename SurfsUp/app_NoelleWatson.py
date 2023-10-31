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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

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
        f"Welcome to my climate api!<br/></br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start_date_yyyy-mm-dd)<br/>"
        f"/api/v1.0/(start_date_yyyy-mm-dd)/(end_date_yyyy-mm-dd)"    
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session link from Python to DB
    session = Session(engine)
 
    # Take year_from_recent from climate.ipynb
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Find precipitaion data for past year of data
    precip_year_prior = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_prior).all()

    # Close session after query
    session.close()

    # Convert to dictionary
    precip = []
    for date, prcp in precip_year_prior:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip.append(precip_dict)
    
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create session link from Python to DB
    session = Session(engine)

    # Find list of all stations
    stations = session.query(Station.station).all()

    # Close session after query
    session.close()

    # Return list of stations
    stations = list(np.ravel(stations))
    return jsonify(stations)

@app.route("/api/v1.0/tobs") 
def tobs():
    # Create session link from Python to DB
    session = Session(engine)

    # Find dates and temperature observations of the most active station for the past year
    year_from_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station_tobs = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= year_from_recent).all()

    # Close session after query
    session.close()

    # Return list
    tobs = list(np.ravel(most_active_station_tobs))
    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    # Start engine
    session = Session(engine)

    # Create select parameters
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Find information based on start date entered
    start_date = session.query(*sel).filter(Measurement.date >= start).group_by(Measurement.date).order_by(Measurement.date).all()
    
    # Close session after query
    session.close()

    # Create an empty dictionary
    start_date_dict = {}

    for date, min_temp, avg_temp, max_temp in start_date:
        start_date_dict[date] = (min_temp, avg_temp, max_temp)
            
    return jsonify(start_date_dict)    
    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Start engine
    session = Session(engine)

    # Create select parameters
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Find information based on start/end dates entered
    startend_date = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).order_by(Measurement.date).all()

    # Close session after query
    session.close()

    # Create an empty dictionary
    startend_date_dict = {}

    for date, min_temp, avg_temp, max_temp in startend_date:
        startend_date_dict[date] = (min_temp, avg_temp, max_temp)
            
    return jsonify(startend_date_dict) 


if __name__ == '__main__':
    app.run(debug=True)