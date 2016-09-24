from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import urllib2
import datetime
import json
import config


app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

deltaAPIBaseUrl = 'https://demo30-test.apigee.net/v1/hack/'
apiKey = config.deltaKey

currentOverHeadVolume = 0
totalOverHeadVolume = 0

# Dict to store type to volume mapping
typeToVolumeMap = []

# Current flight number
flightNumber = 1988

# Current time
now = datetime.datetime.now()

if __name__ == '__main__':
    socketio.run(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('flight info query')
def handle_my_flight_info_query(json):
   	flightnumber = json['flightnumber']
   	print getAircraftType(getFlightStatus(flightnumber))

def getFlightStatus(flightNumber):
	date = now.strftime("%Y-%m-%d")
	url = deltaAPIBaseUrl + "status?flightNumber=" + flightNumber + "&flightOriginDate=" + date + "&apikey=" + apiKey
	print url
	response = urllib2.urlopen(url)
	data = response.read()
	j = json.loads(data)
	return j

def getAircraftType(j):
	equipmentType = j['flightStatusResponse']['statusResponse']['flightStatusTO']['flightStatusLegTOList']['equipmentType']
	return equipmentType

