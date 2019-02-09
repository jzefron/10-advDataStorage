
#from flask import Flask
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy.pool import NullPool

engine = create_engine("sqlite:///Resources/hawaii.sqlite",
                poolclass=NullPool)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
lDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
session.close()
bDate = dt.datetime.strptime(lDate[0],"%Y-%m-%d") - dt.timedelta(days=365)
# Create our session (link) from Python to the DB

#inspector = inspect(engine)
def calc_temps(start_date, end_date = lDate[0]):
    session = Session(engine)
    res = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    return (res)


app = Flask(__name__)

@app.route('/')
def hello_world():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startDate<br/>"
        f'/api/v1.0/startDate/endDate<br/>'
    )
@app.route('/api/v1.0/stations')
def station():
    session = Session(engine)
    res = jsonify(session.query(Station.station).all())
    session.close()
    return res

@app.route('/api/v1.0/precipitation')
def pr():
    
    session = Session(engine)
    
    prcp_date = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= bDate).order_by(Measurement.date).all()
    # Save the query results as a Pandas DataFrame and set the index to the date column
    prDf = pd.DataFrame(prcp_date)
    prDf_clean = prDf.dropna()
    # Sort the dataframe by date
    #prDf_clean['date'] = pd.to_datetime(prDf_clean['date'])
    prDf_clean  = prDf_clean.set_index('date')
    prDict = prDf_clean.to_dict('dict')
    res = jsonify(prDict)
    session.close()
    return(res)

@app.route('/api/v1.0/tobs')
def temp():
    session = Session(engine)
    tops_date = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= bDate).order_by(Measurement.date).all()
    session.close()
    tDf = pd.DataFrame(tops_date)
    tDf_clean = tDf.dropna()
    tDf_clean = tDf_clean.set_index('date')
    tDict = tDf_clean.to_dict('dict')
    res = jsonify(tDict['tobs'])
    return(res)

@app.route('/api/v1.0/<start>')
def beg(start):
    ans = calc_temps(start)
    return(jsonify(ans))

@app.route('/api/v1.0/<start>/<end>')
def range(start,end):
    ans = calc_temps(start,end)
    return(jsonify(ans))

 
if __name__ == '__main__':
    app.run(debug=True)
