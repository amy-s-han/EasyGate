from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import urllib2
import datetime
import json
import config


app = Flask(__name__)
socketio = SocketIO(app)

deltaAPIBaseUrl = 'https://demo30-test.apigee.net/v1/hack/'
apiKey = config.deltaKey

currentOverHeadVolume = 0
totalOverHeadVolume = 0

# Dict to store type to volume mapping
simpleBinDims = dict()

simpleBinDims["M90"] = (55,15,12,39,1)
simpleBinDims["M88"] = (54,20,11,36,1)
simpleBinDims["738"] = (58,15,12,33,1)
simpleBinDims["73H"] = (58,15,12,33,1)
simpleBinDims["73W"] = (58,15,12,28,1)
simpleBinDims["739"] = (58,15,12,37,1)
simpleBinDims["752"] = (58,15,12,45,1)
simpleBinDims["7S8"] = (58,15,12,30,1)
simpleBinDims["753"] = (58,15,12,49,1)
simpleBinDims["757"] = (58,15,12,45,1)
simpleBinDims["75W"] = (58,15,12,44,1)
simpleBinDims["76W"] = (40,14,13,41,2)
simpleBinDims["763"] = (40,14,13,41,2)
simpleBinDims["764"] = (40,14,13,45,2)
simpleBinDims["773"] = (42,20,18,52,2)
simpleBinDims["777"] = (42,20,18,57,2)
simpleBinDims["AT7"] = (42, 8,14,17,1)
simpleBinDims["CR7"] = (43,16, 8,17,1)
simpleBinDims["CRJ"] = (43,16, 8,14,1)
simpleBinDims["EM2"] = (31,16, 8,11,1)
simpleBinDims["RJ9"] = (42,12,12,11,1)
simpleBinDims["ERJ"] = (63,20,9,18, 1)
simpleBinDims["ER3"] = (63,20,9,22, 1)
simpleBinDims["E70"] = (24,16,10,18,1)
simpleBinDims["E75"] = (24,16,10,20,1)

# Current flight number
flightNumber = 1988

# Current time
now = datetime.datetime.now()

if __name__ == '__main__':
    socketio.run(app)

@app.route('/')
def index():
    return render_template('estimator.html')

@socketio.on('flight_info_query')
def handle_my_flight_info_query(json):
   	flightnumber = json['flightnumber']
   	flightStatusJSON = getFlightStatus(flightnumber)
   	if flightStatusJSON != None:
   		aircraftType = getAircraftType(flightStatusJSON)
   		if aircraftType in simpleBinDims:	

            dimensions = simpleBinDims[aircraftType]
            
   			print aircraftType, " has these dimensions: ", simpleBinDims[aircraftType]
   		else:
   			emit('flight_info_query_fail', { "error": "No dimension info on that flight's aircraft"})
   		#print aircraftType, dim 
   	else:
   		emit('flight_info_query_fail', { "error": "That flight number does not exist"})

def getFlightStatus(flightNumber):
	date = now.strftime("%Y-%m-%d")
	url = deltaAPIBaseUrl + "status?flightNumber=" + flightNumber + "&flightOriginDate=" + date + "&apikey=" + apiKey
	print url
	response = urllib2.urlopen(url)
	if response.getcode() == 200:
		rawData = response.read()
		jsonData = json.loads(rawData)
		status = jsonData['flightStatusResponse']['status']
		if status == "FAIL":
			return None
		return jsonData
	else:
		return None

def getAircraftType(j):
	equipmentType = j['flightStatusResponse']['statusResponse']['flightStatusTO']['flightStatusLegTOList']['equipmentCodeDelta']
	return equipmentType

