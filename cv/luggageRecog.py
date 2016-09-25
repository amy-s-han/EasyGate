#!/usr/bin/env python
import numpy as np
import cv2
import utils
import sys
sys.path.append('../cvk2')
import cvk2
import microsoftCVHelpers as msCV


# Variables

_key = 'e80f8ece393f4eebb3d98b0bb36f04d0'

bagTypes = ['bag', 'backpack', 'bags', 'handbag', 'accessory']
luggageTypes = ['suitcase', 'luggage'] + bagTypes
bagMotions = ['holding', 'carrying']


if __name__ == "__main__":

	orig = cv2.imread('testPictures/womanWithBackpackSide.jpg')

	h = orig.shape[0] #get height
	w = orig.shape[1] #get width
	# cvk2.labelAndWaitForKey(orig, 'Original')

	# Load raw image file into memory
	pathToFileInDisk = 'testPictures/womanWithBackpackSide.jpg'
	with open( pathToFileInDisk, 'rb' ) as f:
	    data = f.read()
	   
	# Computer Vision parameters
	params = { 'visualFeatures' : 'Categories, Tags, Description, Faces'} 

	headers = dict()
	headers['Ocp-Apim-Subscription-Key'] = _key
	headers['Content-Type'] = 'application/octet-stream'

	json = None

	result = msCV.processRequest(json, data, headers, params )

	if result is not None:

		# Load the original image, fetched from the URL
		data8uint = np.fromstring( data, np.uint8 ) # Convert string to an unsigned int array
		img = cv2.cvtColor( cv2.imdecode( data8uint, cv2.IMREAD_COLOR ), cv2.COLOR_BGR2RGB )

		# in reverse order: lowest confidence -> highest confidence
		tags = sorted(result['tags'], key=lambda x: x['confidence'])

		description = result['description']
		caption = description['captions'][0]['text']

		print "\n\n", caption
		print "\n\n", description['tags']

		luggagePresent = []
		bagBool = False
		suitcaseBool = False


		for i in caption.split():
			if i in bagMotions:
				bagBool = True
				break

			elif i in luggageTypes:
				if i in bagTypes:
					bagBool = True
					break

				else:
					suitcaseBool = True


		if not bagBool and not suitcaseBool:
			for i in description['tags']:

				if i in luggageTypes:
					if i in bagTypes:
						bagBool = True
						print "bag true"

						break
					suitcaseBool = True
					print "suitcase true"

					break

		if bagBool:
			luggagePresent.append("bag")
		if suitcaseBool:
			luggagePresent.append("suitcase")
		

		print luggagePresent

		cvk2.labelAndWaitForKey(img, 'img')
