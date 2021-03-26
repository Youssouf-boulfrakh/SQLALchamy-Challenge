#import dependencies
from flask import Flask,json,jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session,scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into ORM classes.
Base = automap_base()
# Reflect the tables.
Base.prepare(engine, reflect=True)

# Save reference to the tables.
Measurement = Base.classes.measurement
Station = Base.classes.station
Base.classes.keys()

#save table references
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create our session (link) from Python to the DB
session = scoped_session(sessionmaker(bind=engine))

# Find the last date
latest_date_in_db = session.query(Measurement.date).\
order_by(Measurement.date.desc()).first().date
start_date_in_db = session.query(Measurement.date).\
order_by(Measurement.date).first().date
one_year_ago = dt.datetime.strptime(latest_date_in_db, '%Y-%m-%d') - dt.timedelta(days=365)
# Storing the year ago date in YYYY-MM-DD format for further analysis
one_year_ago_date = one_year_ago.strftime('%Y-%m-%d')
# Calculate most active station
most_active_station = session.query(Station.station, func.count(Measurement.station)).\
filter(Station.station == Measurement.station).\
group_by(Station.station).order_by(func.count(Measurement.station).desc()).first()
# Setup Flask
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    return (
        f"<h1>Welcome to the Climate App API!</h1>"
        f"<h1>Step 2 - Climate App</h1>"
        f"This is a Flask API for Climate Analysis .<br/><br/><br/>"
        f"<img width='600' src='https://www.surfertoday.com/images/stories/tube-time.jpg'/ >"
        f"<br/>"
        f"<br/>--List of all the routes that are available--<br/>"
        f"<br/>Returns the dates and rainfall(precipitation) for the previous year.<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>Returns a list of stations.<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>Returns a list of Temperature for the previous year for the most active station.<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>Returns the minimum, average and maximum temperature for a date.<br/>"
        f"/api/v1.0/start_date<br/>"
        f"<br/>Returns the minimum, average and maximum temperature for a start and end date.<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"<br/>-Dates are in YYYY-MM-DD format"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON representation of a dictionary where the date is the key and the value is 
    the precipitation value"""
    print("Received precipitation api request.")
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago_date).\
    filter(Measurement.prcp != None).\
    order_by(Measurement.date).all()
    #prepare the dictionary with the date as the key and the prcp value as the value
    precipitation_dict = dict(precipitation_data)
    # Return JSON Representation of Dictionary
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
#"""Return a list of stations."""
    print("Received station api request.")
    station_data = session.query(Station.station, Station.name).order_by(Station.station).all()
    station_dict = dict(station_data)
    return jsonify(station_dict)    

@app.route("/api/v1.0/tobs")
#Calculate most active station
def temps_last_yr():
#"""Return a JSON list of temperature observations for the previous year."""
    print("Received tobs api request.")
    temps_last_yr_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= one_year_ago_date).\
    filter(Measurement.station == most_active_station[0]).order_by(Measurement.date).all()
    temps_last_yr_dict = dict(temps_last_yr_data)
    # Return the JSON representation of dictionary.
    return jsonify(temps_last_yr_dict)

@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def temps_from_date(start,end):
#"""Return a JSON list of the minimum, average, and maximum temperatures from the start date unitl the end date."""
    
    # If we have both a start date and an end date.
    if end != None:
        print("Received start date and end date api request.")
        # Set up for user to enter dates
        if start > latest_date_in_db or start < start_date_in_db\
            or end > latest_date_in_db or end < start_date_in_db:
            return(f"Select date range between {start_date_in_db} and {latest_date_in_db}")
        else:
            # Query Min, Max, and Avg based on dates
            day_temp2 = session.query(func.min(Measurement.tobs),\
            func.round(func.avg(Measurement.tobs)),\
            func.max(Measurement.tobs)).\
            filter(Measurement.date>=start).filter( Measurement.date<=end).all()
            dict2 = {"Min_Temp": day_temp2[0][0], "Avg_Temp": day_temp2[0][1], "Max_Temp": day_temp2[0][2]}
            return jsonify(dict2)
    # If we only have a start date.
    else:
        print("Received start date api request.")
        # Set up for user to enter dates
        if start > latest_date_in_db or start < start_date_in_db:
            return(f"Select date on or after {start_date_in_db} or before {latest_date_in_db}")
        else:
            day_temp1 = session.query(func.min(Measurement.tobs),\
            func.round(func.avg(Measurement.tobs)),\
            func.max(Measurement.tobs)).\
            filter(Measurement.date>=start).all()
            dict1 = {"Min_Temp": day_temp1[0][0], "Avg_Temp": day_temp1[0][1], "Max_Temp": day_temp1[0][2]}
            # Return the JSON representation of dictionary.
            return jsonify(dict1)
    #Code to actually run
if __name__ == "__main__":
    app.run(debug = True)