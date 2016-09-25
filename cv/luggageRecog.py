#!/usr/bin/env python
import numpy as np
import cv2
import utils
import sys
sys.path.append('../cvk2')
import cvk2
import microsoftCVHelpers as msCV
import json


# Variables

_key = 'e80f8ece393f4eebb3d98b0bb36f04d0'

if __name__ == "__main__":

	orig = cv2.imread('testPictures/manWithSuitcase0.jpg')

	h = orig.shape[0] #get height
	w = orig.shape[1] #get width
	# cvk2.labelAndWaitForKey(orig, 'Original')

	# Load raw image file into memory
	pathToFileInDisk = 'testPictures/noisyManWithSuitcase.jpg'
	with open( pathToFileInDisk, 'rb' ) as f:
	    data = f.read()
	   
	print "TYPE OF DATA: ", type(data)

	pathToFileInDisk = 'testPictures/manWithSuitcase0.jpg'
	with open( pathToFileInDisk, 'rb' ) as f:
	    data = f.read()
	    
	# Computer Vision parameters
	params = { 'visualFeatures' : 'Categories, Tags, Description, Faces'} 

	headers = dict()
	headers['Ocp-Apim-Subscription-Key'] = _key
	headers['Content-Type'] = 'application/octet-stream'

	json = None

	result = msCV.processRequest( json, data, headers, params )

	if result is not None:
		print result

		# Load the original image, fetched from the URL
		data8uint = np.fromstring( data, np.uint8 ) # Convert string to an unsigned int array
		img = cv2.cvtColor( cv2.imdecode( data8uint, cv2.IMREAD_COLOR ), cv2.COLOR_BGR2RGB )

		# in reverse order: lowest confidence -> highest confidence
		tags = sorted(result['tags'], key=lambda x: x['confidence'])

		description = result['description']

		print "\n\nNow tag: \n\n", tags

		print "\n\nDescription: \n\n", description

		print "\n\n", description['captions'][0]['text']
		print "\n\n", description['tags']

		for i in description['tags']:
			print i

		
		msCV.renderResultOnImage( result, img )

		# in reverse order: lowest confidence -> highest confidence
		tags = sorted(result['tags'], key=lambda x: x['confidence'])

		print "\n\nNow: \n\n", tags

		# ig, ax = plt.subplots(figsize=(15, 20))
		# ax.imshow( img )

		cvk2.labelAndWaitForKey(img, 'img')
