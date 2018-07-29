import datetime as datetime
from datetime import date
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# find last date with records in the DB and calculate first date for the 12 month period
def find_date():
    prcp_data = session.query(Measurement.date) \
                   .distinct(Measurement.date) \
                   .order_by(desc(Measurement.date)) \
                   .first() 


    for row in prcp_data:
        last_date = row
    
# # Subract 1 year from the last date of measurements to find the beginning date for our query
    last_date_obj = datetime.datetime.strptime(last_date, "%Y-%m-%d")
    first_date_obj = last_date_obj.replace(last_date_obj.year - 1)


    first_date = str(first_date_obj.date())
    
    return first_date
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
        f"/api/v1.0/start_date"
        
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of the last 12 months of precipitation data"""
    # Find the last date of measurements in the database and record it
    tmp_date = find_date()
    
    # Design a query to retrieve the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp) \
                   .filter(Measurement.date >= tmp_date) \
                   .order_by(Measurement.date) \
                   .all()
   # Create a dictionary from the row data and append to a list of precipitation measurements
    measurement_prcp = []
    for measurement in results:
        
        measurement_prcp.append(measurement._asdict())

    return jsonify(measurement_prcp)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def temperature():
    """Return a list of the last 12 months of temperature data"""
    # Find the last date of measurements in the database and record it
    tmp_date = find_date()
    
    # Design a query to retrieve the last 12 months of temperature data
    results = session.query(Measurement.date, Measurement.tobs) \
                     .filter(Measurement.date >= tmp_date) \
                     .order_by(Measurement.date) \
                     .all()
   # Create a dictionary from the row data and append to a list of temperature measurements
    measurement_tobs = []
    for measurement in results:
       
        measurement_tobs.append(measurement._asdict())

    return jsonify(measurement_tobs)

@app.route("/api/v1.0/start_date")
def start_date():
    """Return min, avg and max of last 12 months of temperature data"""
    # Find the last date of measurements in the database and record it
    tmp_date = find_date()
    
    # Design a query to retrieve the last 12 months of temperature data and get min, avg and max values
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
                     .filter(Measurement.date >= tmp_date) \
                     .all()
   # Convert list of tuples into normal list
    temp = list(np.ravel(results))

    return jsonify(temp)


if __name__ == "__main__":
    app.run(debug=True)