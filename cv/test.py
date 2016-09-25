#!/usr/bin/env python
import numpy as np
import cv2
import utils
import urllib 

def testCam():
	sourceTop = utils.SingleCameraHardware(0) # Init top camera

	from utils import SingleCameraHardware

	if __name__ == "__main__":

		sourceTop = SingleCameraHardware(0) # Init top camera
		sourceTop.loadCalibrationData()

		while True:

			sourceTop.update(Display=True)

			if cv2.waitKey(1) == 113:
				break

		sourceTop.release()


def testLoadVideoFromFile():
	source = cv2.VideoCapture('testVideo/suitcaseFront.mp4')
	source = cv2.VideoCapture('http://128.61.125.170:8080/video')
	blobtracker = utils.simpleBlobTracker(source)

	print "width: ", source.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
	print "height: ", source.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

	cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
	cv2.resizeWindow("frame", 1920, 1080)

	while(source.isOpened()):
		print "video sucessfully playing"

		retval, frame = source.read()

		# blobtracker.blobMaker(frame, True)

		# Detect ticket scanned

		if retval:
			cv2.imshow('frame', frame)
		else:
			break

		while cv2.waitKey(15) < 0: pass	

	source.release()
	cv2.destroyAllWindows()


def streamVideoFromWeb():
	stream=urllib.urlopen('http://128.61.125.170:8080/video')
	bytes=''
	while True:
	    bytes+=stream.read(1024)
	    a = bytes.find('\xff\xd8')
	    b = bytes.find('\xff\xd9')
	    if a!=-1 and b!=-1:
	        jpg = bytes[a:b+2]
	        bytes= bytes[b+2:]
	        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
	        cv2.imshow('i',i)
	        if cv2.waitKey(1) ==27:
	            exit(0)   

	source.release()
	cv2.destroyAllWindows()


if __name__ == "__main__":

	#testCam()
	# testLoadVideoFromFile()
	streamVideoFromWeb()
