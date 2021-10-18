# Dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, request, jsonify

# Database setup
path = "/Users/yol/Desktop/BOOTCAMP/08_SQL_ADVANCED/sqlalchemy-challenge/data/hawaii.sqlite"
engine = create_engine(f"sqlite:///{path}")

# Reflect existing database ito a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def index():
    return (
		f'<h1>Welcome to the Climate API!</h1>'
		f'<p>Here are some of the available options you can use:</p>'
		f'<ul>'
			f'<li><a href="http://127.0.0.1:5000/api/v1.0/precipitation">Daily precipitation rates with /precipitation</a></li>'
			f'<li><a href="http://127.0.0.1:5000/api/v1.0/stations">Available weather stations with /stations</a></li>'
			f'<li><a href="http://127.0.0.1:5000/api/v1.0/tobs">Temperature observations for past 12 months with /tobs</a></li>'
			f'<li><a href="http://127.0.0.1:5000/api/v1.0/start?start_date=2013-01-01">Temperature stats for dates greater than &ltstart_date&gt with /start?start_date=YYYY-MM-DD</a></li>'
			f'<li><a href="http://127.0.0.1:5000/api/v1.0/between?start_date=2015-01-01&end_date=2016-12-31">Temperature stats for dates between &ltstart_date&gt and &ltend_date&gt with /between?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD</a></li>'
		f'</ul>'
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation')
def precipitation():
	session = Session(engine)
	prcp_results = session.query(Measurement.date, Measurement.prcp).group_by(Measurement.date).order_by(Measurement.date.desc()).all()
	session.close()
	all_prcp = []
	for date, prcp in prcp_results:
		prcp_dict = {}
		prcp_dict['date'] = date
		prcp_dict['prcp'] = prcp
		all_prcp.append(prcp_dict)
	return jsonify(all_prcp)

# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
	session = Session(engine)
	station_results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).group_by(Station.id).all()
	session.close()
	all_stations = []
	for station, name, latitude, longitude, elevation in station_results:
		station_dict = {}
		station_dict['station'] = station
		station_dict['name'] = name
		station_dict['latitude'] = latitude
		station_dict['longitude'] = longitude
		station_dict['elevation'] = elevation
		all_stations.append(station_dict)
	return jsonify(all_stations)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
	session = Session(engine)
	most_active = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).limit(1).all()[0][0]
	most_recent = session.query(Measurement.date).filter(Measurement.station == most_active).order_by(Measurement.date.desc()).limit(1).all()[0][0]
	this_year = dt.datetime.strptime(most_recent, '%Y-%m-%d')
	year_ago = this_year - dt.timedelta(days=365)
	tobs_results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.date >= year_ago) & (Measurement.station == most_active)).all()
	session.close()
	all_tobs = []
	for date, tobs in tobs_results:
		tobs_dict = {}
		tobs_dict['date'] = date
		tobs_dict['tobs'] = tobs
		all_tobs.append(tobs_dict)
	return jsonify(all_tobs)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route('/api/v1.0/start', defaults={'start_date':'2013-01-01'})
@app.route('/api/v1.0/start')
def start():
	session = Session(engine)
	start_date = request.args['start_date']
	start_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
	session.close()
	all_start = []
	for min, max, avg in start_results:
		start_dict = {}
		start_dict['TMIN'] = min
		start_dict['TMAX'] = max
		start_dict['TAVG'] = avg
		all_start.append(start_dict)
	return jsonify(all_start)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route('/api/v1.0/between', defaults={'start_date':'2015-01-01', 'end_date':'2016-12-31'})
@app.route('/api/v1.0/between')
def between():
	session = Session(engine)
	start_date = request.args['start_date']
	end_date = request.args['end_date']
	between_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter((Measurement.date >= start_date) & (Measurement.date <= end_date)).all()
	session.close()
	all_between = []
	for min, max, avg in between_results:
		between_dict = {}
		between_dict['TMIN'] = min
		between_dict['TMAX'] = max
		between_dict['TAVG'] = avg
		all_between.append(between_dict)
	return jsonify(all_between)

if __name__ == "__main__":
    app.run(debug=True)