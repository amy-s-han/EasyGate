########################################################################
# File: daRealThing.py - launches parallel threads to stream multiple live web
#	feeds to count baggage types and predict overhead space capacity at  
#   boarding gates. When the ticket agent scans a ticket, a message is sent to
#   us through udp and the threads each grab a frame from their respective 
#   camera feeds and sends them to Microsoft's Cognitive Services Computer
#   Vision API for tagging and captioning. If there is a suitcase or bag in the
#   picture, this program sends this information over to the ticket agent so 
#   that he/she can be informed about how full the overhead bins are and decide
#   whether the piece of luggage should be checked in.
# 
# Author: Amy Han
# Geogia Tech Hackathon September 2017
########################################################################

#!/usr/bin/env python
import sys
sys.path.append('../cvk2')
import cvk2
import cv2
import httplib
import microsoftCVHelpers as msCV
import numpy as np
import requests
import socket
import threading
import urllib
import utils
 

# global vars - yea i know that the variable names aren't consistent...

bagTypes = ['bag', 'backpack', 'bags', 'handbag', 'accessory']
luggageTypes = ['suitcase', 'luggage'] + bagTypes
bagMotions = ['holding', 'carrying']

_key = 'e80f8ece393f4eebb3d98b0bb36f04d0'
NUM_CAMS = 1
webpageIP = 'http://128.61.66.76:5000'
# webpageIP = 'http://143.215.102.40:5000'


def processImages(img):
	# Computer Vision parameters
	params = { 'visualFeatures' : 'Categories, Tags, Description, Faces'} 

	headers = dict()
	headers['Ocp-Apim-Subscription-Key'] = _key
	headers['Content-Type'] = 'application/octet-stream'

	json = None

	img_str = cv2.imencode('.jpg', img)[1].tostring()
	result = msCV.processRequest( json, img_str, headers, params)

	return result

def idLuggage(img):
	luggagePresent = ""
	msResults = processImages(img)

	if msResults is not None:

		# in reverse order: lowest confidence -> highest confidence
		tags = sorted(msResults['tags'], key=lambda x: x['confidence'])
		
		description = msResults['description']
		caption = description['captions'][0]['text']	

		bagBool = False
		suitcaseBool = False

		for i in caption.split():

			if i in luggageTypes:
				if i in bagTypes:
					bagBool = True
					break

				else:
					suitcaseBool = True


		if not bagBool and not suitcaseBool:
			for i in description['tags']:
				print i

				if i in luggageTypes:
					if i in bagTypes:
						bagBool = True
						print "bag true"

						break
					suitcaseBool = True
					print "suitcase true"

					break

		if bagBool:
			luggagePresent = "bag"
		if suitcaseBool:
			luggagePresent = "suitcase"
		

		print "The luggage present is: ", luggagePresent

	return luggagePresent


def sendToTicketAgent(luggagePresent):
	# POST. "/submitCVResult" 
	print "POSTING TO TICKET AGENT"

	ticketURL = webpageIP + "/submitCVResult"

	if luggagePresent is None or luggagePresent == '':
		luggagePresent.append("no luggage detected")

	retries = 0
	result = None

	while True:

		payload = '{"result": "' + luggagePresent + '"}'
		headers = {'content-type': "application/json", 'cache-control': "no-cache",}
		response = requests.request("POST", ticketURL, data = payload, headers = headers)

		if response.status_code == 429: 

			print( "Message: %s" % ( response.json()['error']['message'] ) )

			if retries <= _maxNumRetries: 
				time.sleep(1) 
				retries += 1
				continue
			else: 
				print( 'Error: failed after retrying!' )
			break

		elif response.status_code == 200 or response.status_code == 201:

			print "success!!!\n"
		else:
			print( "Error code: %d" % ( response.status_code ) )
			print( "Message: %s" % ( response.json()['error']['message'] ) )

		break
        
def runStream(tid, streamURL, debug = False):
	print "Hi I'm a thread with tid: ", tid, " and url: ", streamURL

	stream = urllib.urlopen(streamURL)
	bytes = ''

	if tid == 0:

		ip = "0.0.0.0"
		port = 5005

		sock = socket.socket(socket.AF_INET, # Internet
		         socket.SOCK_DGRAM) # UDP
		sock.bind((ip, port))
		sock.setblocking(0)

	print "here2"

	while True:
		bytes += stream.read(1024)

		a = bytes.find('\xff\xd8')
		b = bytes.find('\xff\xd9')

		if a != -1 and b != -1:
			jpg = bytes[a:b + 2]
			bytes= bytes[b + 2:]
			img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)

			cv2.imshow('img ' + str(tid), img)
			if tid == 0:

				# Check to see if the ticket agent has scanned a ticket:
				try:
					data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
					if data == "TAKEPIC": # ticket was scanned! Go process the picture!
						# print "hi"
						luggagePresent = idLuggage(img)
						sendToTicketAgent(luggagePresent)
				except:
					pass

			# to exit press ESC!
			if cv2.waitKey(1) == 27:
				print "you tried to exit........"
				exit(0)   

	source.release()
	cv2.destroyAllWindows()

if __name__ == "__main__":

	streamURLS = ['http://128.61.31.176:8080/video', 'http://128.61.26.166:8080/video']

	for i in range(NUM_CAMS):
		worker = threading.Thread(target = runStream, args = (i, streamURLS[i]))
		worker.daemon = False
		worker.start()

	if cv2.waitKey(1) == 27:
		exit(0)

	