from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
<<<<<<< HEAD
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

=======
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

simpleBinDims["M90"] = (55,15,12)                              
simpleBinDims["M88"] = (54,20,11)                              
simpleBinDims["738"] = (58,15,12)
simpleBinDims["73H"] = (58,15,12)
simpleBinDims["73W"] = (58,15,12)
simpleBinDims["739"] = (58,15,12)                                                                                                                            
simpleBinDims["752"] = (58,15,12)
simpleBinDims["7S8"] = (58,15,12)
simpleBinDims["753"] = (58,15,12)                                                                                
simpleBinDims["757"] = (58,15,12)
simpleBinDims["75W"] = (58,15,12)                                                                                                                                                                                                                                                                                                                                
simpleBinDims["76W"] = (40,14,13)
simpleBinDims["763"] = (40,14,13)
simpleBinDims["764"] = (40,14,13)                                  
simpleBinDims["773"] = (42,20,18)
simpleBinDims["777"] = (42,20,18)                                
simpleBinDims["AT7"] = (42,8 ,14)                                  
simpleBinDims["CR7"] = (43,16,8 )                                  
simpleBinDims["CRJ"] = (43,16,8 )                                  
simpleBinDims["EM2"] = (31,16,8 )                                  
simpleBinDims["RJ9"] = (42,12,12)                                  
simpleBinDims["ERJ"] = (63,20,9 )                                  
simpleBinDims["ER3"] = (63,20,9 )                                  
simpleBinDims["E70"] = (24,16,10)        
simpleBinDims["E75"] = (24,16,10)

# Current flight number
flightNumber = 1988

# Current time
now = datetime.datetime.now()

>>>>>>> 0b9b8c8ca28997cdaee066be79f9e34aa396a265
if __name__ == '__main__':
    socketio.run(app)

@app.route('/')
def index():
    return render_template('index.html')

<<<<<<< HEAD

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    emit('my event', json)
=======
@socketio.on('flight_info_query')
def handle_my_flight_info_query(json):
   	flightnumber = json['flightnumber']
   	flightStatusJSON = getFlightStatus(flightnumber)
   	if flightStatusJSON != None:
   		aircraftType = getAircraftType(flightStatusJSON)
   		if aircraftType in simpleBinDims:	
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

>>>>>>> 0b9b8c8ca28997cdaee066be79f9e34aa396a265
