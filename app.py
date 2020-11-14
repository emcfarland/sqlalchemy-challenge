import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

@app.route("/")
def welcome():
    return (
        f"Welcome to my project page. Available Routes:<br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    analysis_end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    analysis_start = (dt.datetime.strptime(analysis_end, "%Y-%m-%d").date() - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    results = session.query(Measurement.date, Measurement.prcp).\
                            filter(Measurement.date >= analysis_start).\
                            group_by(Measurement.date).\
                            order_by(Measurement.date).all()

    session.close()

    precip = dict(results)

    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).distinct().all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def all_temps():
    session = Session(engine)

    analysis_end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    analysis_start = (dt.datetime.strptime(analysis_end, "%Y-%m-%d").date() - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    results = session.query(Measurement.tobs).\
                            filter(Measurement.station=='USC00519281').\
                            filter(Measurement.date>=analysis_start).\
                            order_by(Measurement.date).all()

    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                            filter(Measurement.date>=start).all()

    session.close()

    temp_dict = {"min": results[0][0], "max": results[0][1], "avg": results[0][2]}

    return jsonify(temp_dict)


@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                            filter(Measurement.date>=start).\
                            filter(Measurement.date<=end).all()

    session.close()

    temp_dict = {"min": results[0][0], "max": results[0][1], "avg": results[0][2]}

    return jsonify(temp_dict)


if __name__ == '__main__':
    app.run(debug=True)
