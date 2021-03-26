#Import dependencies

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Use Flask to create your routes.
from flask import Flask, jsonify


#Home page.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

precipitation = Base.classes.measurement
Station= Base.classes.station

app = Flask(__name__)


#List all routes that are available
@app.route("/")
def homePage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
    )



#Precipitation route

@app.route("/api/v1.0/precipitation")
def prcpAnalysis():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation"""
    # Query all Measures
    results = session.query(precipitation.date, precipitation.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


#stations route
@app.route("/api/v1.0/stations")

def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of Stations"""
    # Query all Stations
    results1 = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation ).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results1))

#Return a JSON list of stations from the dataset.
    return jsonify(all_stations)


#Tobs route
@app.route("/api/v1.0/tobs")

def tobsAnalysis():
    # Create our session (link) from Python to the DB
    session = Session(engine)

#Query the dates and temperature observations of the most active station for the last year of data.
    lastdatapointdate = session.query(precipitation.date).order_by(precipitation.date.desc()).first()
    lastdatapointdate[0]

    yearago= "2016-08-23"
    tobs_active =session.query(precipitation.date, precipitation.tobs).filter(precipitation.date >=yearago).all()

# Convert list of tuples into normal list
    tobs_active = list(np.ravel(tobs_active))

#Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_active)
# call the app
if __name__=='__main__':
    app.run(debug=True)