from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import urllib2
import datetime
import json
import config
import time
import socket
import struct 

initScan = False
result = None

app = Flask(__name__)
deltaAPIBaseUrl = 'https://demo30-test.apigee.net/v1/hack/'
apiKey = config.deltaKey
socketio = SocketIO(app)

currentOverHeadVolume = 0
totalOverHeadVolume = 0
luggageCount = (0, 0)

# Dict to store plane type to volume mapping
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

# Dict to store luggage type to volume mapping
simpleLuggageDims = dict()
simpleLuggageDims["bag"] = (9, 14, 22)
simpleLuggageDims["suitcase"] = (9, 14, 22)
boardingPassIndex = 0
boardingPasses = [('Mark Smith','First','C4','ATL'), ('David Torres','First','C6','ATL'), ('Nicole Brown','First','B6','ATL'), ('Stephen Williams','First','B5','ATL'), ('Becky Brown','First','C3','ATL'), ('Shelby Rowe','First','A1','ATL'), ('John Anderson','First','C5','ATL'), ('Patricia Chapman','First','B4','ATL'), ('Heather Douglas','First','A2','ATL'), ('Deborah Gonzales','First','A4','ATL'), ('Tara Peterson','First','B3','ATL'), ('Thomas Butler','First','C1','ATL'), ('David Moore','First','A5','ATL'), ('Mark Norris','First','A3','ATL'), ('Kelly Powell','First','B1','ATL'), ('Vincent Dawson','First','B2','ATL'), ('Devin Stewart','First','A6','ATL'), ('Derek Hayden','First','C2','ATL'), ('Francis Nguyen','Business','F3','ATL'), ('Sarah Jackson','Business','G4','ATL'), ('Jessica Fowler','Business','D4','ATL'), ('Olivia Mueller','Business','H4','ATL'), ('Sandra Baker','Business','E2','ATL'), ('Daniel Kennedy','Business','F4','ATL'), ('Sarah Greene','Business','G6','ATL'), ('Maria Adams','Business','G3','ATL'), ('Collin Lee','Business','G5','ATL'), ('Christopher Patton','Business','D1','ATL'), ('Valerie Tucker','Business','D3','ATL'), ('Crystal Hardy','Business','F1','ATL'), ('Elizabeth Burgess','Business','G1','ATL'), ('Benjamin Daniel','Business','G2','ATL'), ('Michael Hill','Business','E1','ATL'), ('Rebecca Russell','Business','F2','ATL'), ('Brian Rosales','Business','E3','ATL'), ('Annette Kirk','Business','H5','ATL'), ('Tyler Michael','Business','E4','ATL'), ('Shelly Ellis','Business','D6','ATL'), ('Carla Tucker','Business','H1','ATL'), ('Brittney Powers','Business','F5','ATL'), ('Julia Thomas','Business','F6','ATL'), ('Mrs. Kelly Harris','Business','D5','ATL'), ('Ruth Pierce','Business','E5','ATL'), ('Cassandra Scott','Business','D2','ATL'), ('Jose Molina','Business','E6','ATL'), ('Heather Riddle','Business','H6','ATL'), ('Christina Coffey','Business','H2','ATL'), ('Timothy Myers','Business','H3','ATL'), ('Emily Williams','Economy','L3','ATL'), ('Jessica Dixon','Economy','Z3','ATL'), ('Kevin Allen','Economy','W6','ATL'), ('Sandra Robles','Economy','T3','ATL'), ('Deanna Rodriguez','Economy','N4','ATL'), ('Tammy Barrett','Economy','Z4','ATL'), ('Jamie Fuller MD','Economy','V3','ATL'), ('Brian Jones','Economy','L6','ATL'), ('Michael Mcguire','Economy','Q2','ATL'), ('Thomas Wilkins','Economy','J4','ATL'), ('Brett Martinez','Economy','J3','ATL'), ('Wesley Gaines','Economy','Y2','ATL'), ('Carlos Caldwell','Economy','Y4','ATL'), ('Debra Vega','Economy','T5','ATL'), ('Amanda Thomas','Economy','T1','ATL'), ('Monica Jackson','Economy','R4','ATL'), ('Sarah Pittman DVM','Economy','V2','ATL'), ('Daniel Howard','Economy','O1','ATL'), ('Mrs. Miranda Cox','Economy','S1','ATL'), ('John Riddle','Economy','Q4','ATL'), ('Alyssa Donovan','Economy','N6','ATL'), ('Judith Barnett','Economy','R6','ATL'), ('Melissa Serrano','Economy','Q6','ATL'), ('Christopher Mitchell','Economy','R1','ATL'), ('Laura Lang','Economy','X6','ATL'), ('Denise Rodgers','Economy','J2','ATL'), ('Terry House','Economy','Y3','ATL'), ('Kathleen Burton','Economy','W2','ATL'), ('Jonathan Cruz','Economy','P4','ATL'), ('Victoria Campbell','Economy','N3','ATL'), ('Amanda Rosales','Economy','I5','ATL'), ('Kayla Stone','Economy','Q5','ATL'), ('Daniel Edwards','Economy','W5','ATL'), ('Victor Harris','Economy','V4','ATL'), ('Christopher Gonzalez','Economy','X3','ATL'), ('Lisa King','Economy','U6','ATL'), ('Jenna Anderson','Economy','K1','ATL'), ('William Michael','Economy','R5','ATL'), ('Amber Williams','Economy','I4','ATL'), ('Tonya Green','Economy','I1','ATL'), ('Geoffrey Townsend','Economy','V6','ATL'), ('Patrick Sullivan','Economy','O4','ATL'), ('Linda Martin','Economy','M3','ATL'), ('Lindsey Young','Economy','X5','ATL'), ('Jesus Rodriguez','Economy','Y1','ATL'), ('Michele Miller','Economy','U1','ATL'), ('Mark Richmond','Economy','P1','ATL'), ('Lori Davis','Economy','I6','ATL'), ('Catherine Long','Economy','N5','ATL'), ('Jennifer Hines','Economy','T4','ATL'), ('Kimberly Johnson','Economy','U3','ATL'), ('Kim Pitts','Economy','V5','ATL'), ('Stephanie Campos','Economy','W4','ATL'), ('John Wilson','Economy','I3','ATL'), ('Sharon Rice','Economy','S5','ATL'), ('Dale Anderson','Economy','L4','ATL'), ('Kerry Gentry','Economy','J6','ATL'), ('Megan Lambert','Economy','L5','ATL'), ('Brenda Hall','Economy','O5','ATL'), ('Mark Davis','Economy','T6','ATL'), ('Sarah Parks','Economy','S2','ATL'), ('Jimmy Chan','Economy','U2','ATL'), ('Barry Peterson','Economy','K4','ATL'), ('Elizabeth Collins','Economy','U5','ATL'), ('Charles Castillo','Economy','S6','ATL'), ('Andrew Mason','Economy','M1','ATL'), ('Kenneth Nguyen','Economy','Z1','ATL'), ('Anna Morris','Economy','Z6','ATL'), ('Shirley Henderson','Economy','O3','ATL'), ('Matthew Cook','Economy','X2','ATL'), ('Judith Lopez','Economy','M6','ATL'), ('Kelly Smith','Economy','P3','ATL'), ('Sandra Garcia','Economy','K6','ATL'), ('Charles Berg','Economy','X1','ATL'), ('Alex Smith','Economy','S3','ATL'), ('Gabriel Silva','Economy','R2','ATL'), ('Gwendolyn Williams','Economy','V1','ATL'), ('Andrew Mcpherson','Economy','Y5','ATL'), ('Carlos Drake','Economy','T2','ATL'), ('Thomas Phillips','Economy','N2','ATL'), ('Amber Murray','Economy','J5','ATL'), ('John Richardson','Economy','K3','ATL'), ('Joshua House','Economy','P2','ATL'), ('Justin Meyer','Economy','W1','ATL'), ('Rhonda Ward','Economy','O6','ATL'), ('Chelsea Kirby','Economy','Y6','ATL'), ('Douglas Garcia','Economy','M5','ATL'), ('Ian Nunez','Economy','K2','ATL'), ('Richard Vazquez PhD','Economy','P6','ATL'), ('Kayla Buckley','Economy','K5','ATL'), ('Lisa Brown','Economy','Z2','ATL'), ('Vanessa West','Economy','P5','ATL'), ('Steven Garcia','Economy','N1','ATL'), ('Rachel Small','Economy','Q3','ATL'), ('Dawn Medina','Economy','I2','ATL'), ('Amy Jackson','Economy','X4','ATL'), ('Julia Wolfe','Economy','J1','ATL'), ('Alexis Green','Economy','L1','ATL'), ('Geoffrey Thomas','Economy','S4','ATL'), ('Andre Bailey','Economy','R3','ATL'), ('Kyle Kennedy','Economy','M4','ATL'), ('Melissa Short','Economy','Z5','ATL'), ('Ann Garcia','Economy','L2','ATL'), ('Paige Scott','Economy','Q1','ATL'), ('Steven Bowman Jr.','Economy','U4','ATL'), ('Courtney Keller','Economy','M2','ATL'), ('Alexander Ruiz','Economy','O2','ATL'), ('Carrie Smith','Economy','W3','ATL')]

# Current flight number
flightNumber = 1988


# Current time
now = datetime.datetime.now()

if __name__ == '__main__':
    socketio.run(app)

@app.route('/')
def index():
    return render_template('estimator.html')

@app.route('/submitCVResult', methods=['POST'])
def submitCVResult():
    resultJSON = request.json
    typeOfBag = resultJSON['result']

    volume = 1
    dimensions = simpleLuggageDims[typeOfBag]
    for val in dimensions:
        volume = volume * val

    updateOverheadBinStatus(volume)

    if typeOfBag == "bag":
        luggageCount = (luggageCount[0], luggageCount[1] + 1)
    else:
        luggageCount = (luggageCount[0] + 1, luggageCount[1])
    
    emit("updated_luggage_count", { "bags": luggageCount[1], "suitcases": luggageCount[0] })

    return "lol"

@socketio.on('start_cv')
def handle_start_cv(json):
    # Start CV thread
    pass

@socketio.on('flight_info_query')
def handle_my_flight_info_query(json):
    global totalOverHeadVolume

    flightnumber = json['flightnumber']
    print flightnumber
    flightStatusJSON = getFlightStatus(flightnumber)
    if flightStatusJSON != None:
        aircraftType = getAircraftType(flightStatusJSON)
        if aircraftType in simpleBinDims:	
            dimensions = simpleBinDims[aircraftType]
            volume = 1
            for element in dimensions:
                volume = volume*element
            totalOverHeadVolume = volume
            print "Volume of ", aircraftType, dimensions, " is ", volume
        else:
            print "No dimension info on that flight's aircraft"
            emit('flight_info_query_fail', { "error": "No dimension info on that flight's aircraft"})
		#print aircraftType, dim 
    else:
        print "That flight number does not exist"
        emit('flight_info_query_fail', { "error": "That flight number does not exist"})

@socketio.on('initiate_scan')
def handle_initiate_scan():

    ip = config.CVip # CV's ip address
    port = config.CVport
    message = "TAKEPIC"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (ip, port))

    global boardingPassIndex
    boardingPassData = boardingPasses[boardingPassIndex]
    boardingPassIndex += 1
    boardingPass = {}
    boardingPass['name'] = boardingPassData[0]
    boardingPass['class'] = boardingPassData[1]
    boardingPass['seat'] = boardingPassData[2]
    boardingPass['destination'] = boardingPassData[3]
    emit('passenger_information_update', boardingPass)

    
@socketio.on('override_request')
def handle_override_request(json):
    approved = json['approved']
    if approved == True:
        updateOverheadBinStatus()


def updateOverheadBinStatus(currentLuggageVolume):
    global currentOverHeadVolume
    global totalOverHeadVolume
    currentOverHeadVolume = currentOverHeadVolume + currentLuggageVolume
    percentage = currentOverHeadVolume/totalOverHeadVolume
    emit("new_overhead_volume", percentage)

def getFlightStatus(flightNumber):
    date = now.strftime("%Y-%m-%d")
    url = deltaAPIBaseUrl + "status?flightNumber=" + flightNumber + "&flightOriginDate=" + date + "&apikey=" + apiKey
    print url
    response = urllib2.urlopen(url)
    if response.getcode() == 200:
        rawData = response.read()
        jsonData = json.loads(rawData)
        print jsonData
        status = jsonData['flightStatusResponse']['status']
        if status == "FAIL":
            return None
        return jsonData
    else:
        return None

def getAircraftType(j):
    try:
        equipmentType = j['flightStatusResponse']['statusResponse']['flightStatusTO']['flightStatusLegTOList']['equipmentCodeDelta']
    except:
        equipmentType = j['flightStatusResponse']['statusResponse']['flightStatusTO']['flightStatusLegTOList'][0]['equipmentCodeDelta']
    return equipmentType

