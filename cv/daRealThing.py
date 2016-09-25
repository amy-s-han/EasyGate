#!/usr/bin/env python
import numpy as np
import cv2
import utils
import urllib 
import sys
sys.path.append('../cvk2')
import cvk2
import microsoftCVHelpers as msCV
import threading


luggageTypes = ['suitcase', 'backpack', 'bag']
bagTypes = ['bag', 'bags', 'handbag']
_key = 'e80f8ece393f4eebb3d98b0bb36f04d0'
NUM_CAMS = 2


def processImages(img):
	print "here in processImages"
	# Computer Vision parameters
	params = { 'visualFeatures' : 'Categories, Tags, Description, Faces'} 

	headers = dict()
	headers['Ocp-Apim-Subscription-Key'] = _key
	headers['Content-Type'] = 'application/octet-stream'

	json = None

	img_str = cv2.imencode('.jpg', img)[1].tostring()

	result = msCV.processRequest( json, img_str, headers, params )

	if result is not None:
		print result

		# Load the original image, fetched from the URL
		# data8uint = np.fromstring( data, np.uint8 ) # Convert string to an unsigned int array
		# img = cv2.cvtColor( cv2.imdecode( data8uint, cv2.IMREAD_COLOR ), cv2.COLOR_BGR2RGB )

		# in reverse order: lowest confidence -> highest confidence
		# tags = sorted(result['tags'], key=lambda x: x['confidence'])

		# print "\n\nNow: \n\n", tags

		# ig, ax = plt.subplots(figsize=(15, 20))
		# ax.imshow( img )
		# cvk2.labelAndWaitForKey(img, 'img')

	return result

def idLuggage(img):
	print "here in idLuggage"
	luggagePresent = []

	msResults = processImages(img)

	if msResults is not []:

		# in reverse order: lowest confidence -> highest confidence
		tags = sorted(msResults['tags'], key=lambda x: x['confidence'])
		
		print "\n\nNow tag: \n\n", tags

		description = msResults['description']


		print "\n\nDescription: \n\n", description

		print "\n\n", description['captions'][0]['text']
		print "\n\n", description['tags']

		for i in description['tags']:
			print i

			if i in luggageTypes:
				if 
				luggagePresent.append(i)

	return luggagePresent


def runStream(tid, streamURL, debug = False):
	print "Hi I'm a thread with tid: ", tid, " and url: ", streamURL

	stream = urllib.urlopen(streamURL)
	bytes = ''

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

	        # If detect ticket scan

	        # Fake ticket scan with enter for now
	        if cv2.waitKey(1) == 32:
	        	#ticket was scanned! Go process the picture!
	        	luggagePresent = idLuggage(img)

	        # to exit
	        if cv2.waitKey(1) == 27:
	            exit(0)   

	source.release()
	cv2.destroyAllWindows()
	print "here"


if __name__ == "__main__":

	streamURLS = ['http://128.61.31.176:8080/video', 'http://128.61.26.166:8080/video']

	for i in range(NUM_CAMS):
		worker = threading.Thread(target = runStream, args = (i, streamURLS[i]))
		worker.daemon = False
		worker.start()

	msResults = None

	