#!/usr/bin/env python
import numpy as np
import math
import cv2
import pickle
import Image
import math
import random
import time
import matplotlib.pyplot as plt

#################
# SingleCameraHardware initializes hardware and test displays for hardware - 1 camera

def nothing(x):
    pass

class SingleCameraHardware:
    def __init__(self, indx):

        print 'Initializing camera on indexed port #'+str(indx)
        self.cam = cv2.VideoCapture(indx) # initialize camera
        self.__setupWindow() # Calls window creation
        self.name = '(Camera ' + str(indx) + ')'

        # original settings for horizontal cameras
        self.height = int(self.cam.get(4))
        self.width  = int(self.cam.get(3))

        self.frame = None

        # settings for vertical cameras?
        # self.height = int(self.cam.get(3))
        # self.width  = int(self.cam.get(4))

        self.raw    = True

    def __setupWindow(self): # Initialize debug windows
        print 'Window setup currently disabled. Edit __setupWindow and uncomment the named window frame' #cv2.namedWindow('frame', cv2.WINDOW_NORMAL) # Test display for frame

    def update(self,Display=False): # Frame Processing (With optional display)

        ret, self.frameRaw = self.cam.read() # Grabs raw frame from camera
        #self.frameRaw = cv2.resize(self.frameRaw, (self.width*5,self.height*5))
        if self.raw: # If raw, simply pass frame through.
            self.frame = self.frameRaw.copy()

        else: # If not raw - if we have calibration data - then warp image
            self.frame = cv2.undistort(self.frameRaw, self.cameraMatrix, self.distortionVectors, None, self.sizedCameraMatrix)
            self.frame = self.frame[self.roi[1]:self.roi[1]+self.roi[3], self.roi[0]:self.roi[0]+self.roi[2]]

        if Display: # Optional display. Current issue: Small windows still present even if Display=false
            cv2.imshow('Calibrated Frame, '+self.name, self.frame)

    def loadCalibrationData(self, filename='CalibDataDefault.txt'): # Used to pass in intrinsic params from calibration
        self.sourceFile = open(filename,'r')
        self.ret                = pickle.load(self.sourceFile) # If there is a better way of doing this, please let me know
        self.cameraMatrix       = pickle.load(self.sourceFile)
        self.distortionVectors  = pickle.load(self.sourceFile)
        self.rotationVectors    = pickle.load(self.sourceFile)
        self.translationVectors = pickle.load(self.sourceFile)
        self.sizedCameraMatrix, self.roi= cv2.getOptimalNewCameraMatrix(self.cameraMatrix,self.distortionVectors,(self.width,self.height),1,(self.width,self.height)) #Gets adjusted camera matrix for this size frame

        # original settings for horizontal cameras
        self.width  = int(self.roi[2]) # Reset
        self.height = int(self.roi[3])

        # settings for vertical cameras
        # self.width  = int(self.roi[3]) # Reset
        # self.height = int(self.roi[2])

        self.raw = False
        print '\n--------------------------------\nCalibration loaded on {0}\n--------------------------------\n'.format(self.name)

    def release(self): # Module to kill existing windows
        self.cam.release()
        cv2.destroyAllWindows()

#####################
# StereoHardware initializes hardware and test displays for hardware - 2 cameras

class StereoHardware:
    def __init__(self):
        self.camL = cv2.VideoCapture(1) # initialize left camera
        self.camR = cv2.VideoCapture(2) # initialize right camera
        self.__setupWindow() # Calls window creation

    def __setupWindow(self): # Initialize debug windows
        cv2.namedWindow('frameL', cv2.WINDOW_NORMAL) # Test display for left frame
        cv2.namedWindow('frameR', cv2.WINDOW_NORMAL) # Test display for right frame

    def update(self,Display=False): # Frame Processing (With optional display)
        ret, self.frameL = self.camL.read() # Grabs frames from cameras
        ret, self.frameR = self.camR.read()
        if Display: # Optional display. Current issue: Small windows still present even if Display=false
            cv2.imshow('frameR', self.frameR)
            cv2.imshow('frameL', self.frameL)

    def save(self):
        cv2.imwrite('left.png', self.frameL)
        cv2.imwrite('right.png', self.frameR)

    def release(self): # Module to kill existing windows
        self.camL.release()
        self.camR.release()
        cv2.destroyAllWindows()

#####################
# Detects chessboard (for use in calibration)

class ChessboardDetection:
    def __init__(self, source):
        #self.size = 8 # Size of a square chessboard
        #self.patternSize = ((self.size-1),(self.size-1)) # Inner corner dimensions
        #self.patternSize = (6,9) # Inner corner dimensions
        self.patternSize = (3,3) # Inner corner dimensions
        self.source = source

    def ChessboardDetection(self, Display=False):
        image = self.source.frame
        retval, corners = cv2.findChessboardCorners(image, self.patternSize)
        cv2.drawChessboardCorners(image, self.patternSize, corners, retval) #Draws corner pattern if retval
        if Display:
            cv2.imshow('Detection Output', image) # Option for displaying
        return image

######################
# Tracks white light

class WhiteLightTracker:
    def __init__(self, imageInput):
        self.BlurRadius = 31; # Degree of Gaussian Blur
        self.source = imageInput # Set source

    def tracking(self, Display=False):
        self.imgray = cv2.cvtColor(self.source.frame.copy(), cv2.COLOR_RGB2GRAY) # Greyscale conversion
        # We perform gaussian blur on image. This eliminates noise, and ensures that no lone bright
        # Pixels interfere with our detecting.
        self.BlurredImage = cv2.GaussianBlur(self.imgray, (self.BlurRadius, self.BlurRadius), 0) # Blur image.
        (self.minVal, self.maxVal, self.minLoc, self.maxLoc) = cv2.minMaxLoc(self.imgray) # We obtain information on location of min/max
        if Display:
            cv2.circle(self.BlurredImage, self.maxLoc, 15, (0),2) # Draw indication circle
            cv2.imshow(('Center Located '+self.source.name),self.BlurredImage)
        return self.maxLoc


class simpleBlobTracker:
    def __init__(self, source):
        self.source = source
        self.detector = cv2.SimpleBlobDetector()
        # self.fgbg = cv2.BackgroundSubtractorMOG()


    def blobMaker(self, frame, Display=False):
        # convert to grayscale
        display_gray = np.empty((frame.shape[0], frame.shape[1]), 'uint8')
        cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY, display_gray)
        
        # fgmask = self.fgbg.apply(frame)

        # cv2.imshow('frame',fgmask)
        # k = cv2.waitKey(30) & 0xff

        # Detect blobs.
        keypoints = self.detector.detect(display_gray)
        
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
        frame_with_keypoints = cv2.drawKeypoints(display_gray, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # Show keypoints
        if Display:
            cv2.imshow("Keypoints", frame_with_keypoints)
            cv2.waitKey(0)



# Some code with help from http://docs.opencv.org/master/df/d9d/tutorial_py_colorspaces.html
class ColoredBlobTracker:
    def __init__(self,source):
        self.source = source
        # A reminder - some of these values wrap around. You've probably got a bug! A git issue has been created.
        self.sample = np.array([ 60, 186, 185]) # A refrence HSV for the green pen we used to test
        self.HSVTolerance = np.array([20,60,75])
        self.botOfRange = self.sample-self.HSVTolerance
        self.topOfRange = self.sample+self.HSVTolerance
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(20,20))

    def convertHSV(self, frame, Display=False):
        self.HSVframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if Display:
            cv2.imshow('HSVconvert',self.HSVframe)

    def blobMaker(self, frame, Display=False):
        self.convertHSV(frame)
        self.mask = cv2.inRange(self.HSVframe, self.botOfRange, self.topOfRange)
        self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_CLOSE, self.kernel)
        self.maskedFrame = cv2.bitwise_and(frame, frame, mask = self.mask)

        if Display:
            cv2.imshow(('Mask and orig'),self.maskedFrame)

    def tracking(self, frame, Display=False):
        self.blobMaker(frame, Display)
        (self.contours, _) = cv2.findContours(self.mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.contours = sorted(self.contours, key = cv2.contourArea, reverse = True)
        #print len(self.contours) # Says the number of found contours (not necessarily valid ones...)

        if len(self.contours) is not 0: # This checks to see if there are any blobs
            if self.contours[0].shape[0] > 5: # This makes sure the blobs are valid. There's something hinky afoot, sometimes we get poorly informed contours. See git issue.
                #print self.contours[0].shape[0] # For debug. If low, contour not a valid target. FURTHER UPDATE: this is outputting a list of points on the contour. To get a m00,
                #we need at least 4 points (I think)
                self.biggestBlob = cv2.moments(self.contours[0])
                self.centroidX = int(self.biggestBlob['m10']/self.biggestBlob['m00'])
                self.centroidY = int(self.biggestBlob['m01']/self.biggestBlob['m00'])
                self.centerCoordinate = (self.centroidX, self.centroidY)
                self.centerTaggedImage = frame.copy()
                cv2.circle(self.centerTaggedImage, self.centerCoordinate,30,(19,190,19),10)

                if Display:
                    cv2.imshow(('Center Located for Blob'),self.centerTaggedImage)

                self.centerTaggedImage = self.source.frame.copy()
                cv2.circle(self.centerTaggedImage, self.centerCoordinate,30,(19,190,19),10)

                return self.centerCoordinate
        #     else:
        #         print 'invalid blob discarded'
        # else:
        #     print 'no blobs found'



## A class to detect and read qr codes
# I'm not going to lie, the entire zbar package is magic to me
class QRTracking:
    def __init__(self,name):
        self.name = name
        #self.source = source
        #self.source.name = 'for zbartest'

    def tracking(self, source, Display=False):
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable') # Sets up the zbar scanner
        #self.gray = cv2.cvtColor(self.source.frame, cv2.COLOR_BGR2GRAY,dstCn=0) Restore this
        self.gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY,dstCn=0)
        self.pil = Image.fromarray(self.gray)
        self.pilWidth, self.pilHeight = self.pil.size
        self.raw = self.pil.tostring()
        self.image = zbar.Image(self.pilWidth, self.pilHeight, 'Y800', self.raw)
        self.scanner.scan(self.image) # Magic happens
        # Now we have to display the results
        #self.displayLoc = self.source.frame.copy()
        self.displayLoc = source.copy() # Temp for testing purposes

        for symbol in self.image:
            #print dir(symbol)
            if symbol.data == "None":
                print 'Error: Tag without readability' # Could this happen? Probably not
            else:
                #print symbol.location
                self.tagColor = () # Set up empty tuple

                for color in range(3): # The point of this is to ID tags differently via color
                    random.seed(symbol.data+str(color*245))
                    self.tagColor = self.tagColor + ((int(random.random()*254)),)

                for point in symbol.location:
                    cv2.circle(self.displayLoc, point, 5, self.tagColor, -1)

                self.center = (int((symbol.location[0][0]+symbol.location[1][0]+symbol.location[2][0]+symbol.location[3][0])/4), int((symbol.location[0][1]+symbol.location[1][1]+symbol.location[2][1]+symbol.location[3][1])/4))
                #print self.center
                cv2.circle(self.displayLoc, self.center, 7, self.tagColor, -1)
                #ret, baseline = cv2.getTextSize(symbol.data, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
                #spacing = int(np.linalg.norm( np.subtract(symbol.location[3],symbol.location[0]) ))
                #scale = spacing/(baseline*10)
                #cv2.putText(self.displayLoc, symbol.data, symbol.location[3], cv2.FONT_HERSHEY_SIMPLEX, scale, self.tagColor, scale)

            if Display:
                cv2.imshow(('Center Located '+self.name), self.displayLoc)

            return self.center

        if self.image is None:
            print 'Got nothing, boss'


class tagTracking: #pulled from a592dc4 on Oct 3, 2015
    def __init__(self, source):
        self.source = source
        self.RequiredGenerations = 4

    def countGenerations(self,hierarchy,startPoint): #This function counts how many generations down the hierarchy tree goes
        self.currentIndx = startPoint # We initialize at our starting point
        self.Generations = 1

        while True:
            if (hierarchy[0,self.currentIndx,2] != -1 ):
                self.Generations +=1
                self.currentIndx = hierarchy[0,self.currentIndx,2]
                #print 'next generation detected'
            else:
                #print 'last child found'
                return self.Generations

    def tracking(self, threshVal, Display=False):
        self.imgray = cv2.cvtColor(self.source.frame,cv2.COLOR_BGR2GRAY) # Thresholding means greyscale!
        self.ret,self.thresh = cv2.threshold(self.imgray,threshVal,255,0) # We apply our threshold. We are taking input through threshVal from a slider currently. To be implemented: adaptive threshold.
        #self.thresh = cv2.adaptiveThreshold(self.imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,threshVal,2)

        # Second flag in next line: hierarchy flag. RETR_EXTERNAL gives only biggest. RETR_CCOMP gives donuts. RETR_TREE gives full hierarchy. That's what we'll use.
        self.contours, self.hierarchy = cv2.findContours(self.thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        self.countourDisplay = self.source.frame.copy() # Make a display copy.

        self.center = []

        #cv2.drawContours(self.countourDisplay, self.contours, -1, (0,0,255), 3) # Sketch out all contours. Uncomment for debug, to see ALL detected contours.

        if self.hierarchy is not None: # Sometimes on boot, frame is blank and hence no hierarchy at all is given. This lets that pass
            self.ListOfRows = range(self.hierarchy.shape[1]) # We set this up beforehand, because we might need to prune it as time goes on (Update: This is deprecated but this might still prove useful)
            for row in self.ListOfRows: #Each row in hierarchy and contours is a contour. We go through all
                if self.countGenerations(self.hierarchy,row) == self.RequiredGenerations: # Current hierarchical geometric chromatics classifier has four detectable contours (Haha, HGMC for short. I've made an acronym!)
                    cv2.drawContours(self.countourDisplay, self.contours, row, (0,255,0), 3)
                    self.momentData = cv2.moments(self.contours[row])
                    self.cx = int(self.momentData['m10']/self.momentData['m00'])
                    self.cy = int(self.momentData['m01']/self.momentData['m00'])
                    cv2.circle(self.countourDisplay, (self.cx, self.cy) ,15,(0,0,255),-1) # Draw tracking target for display purposes
                    tup = (self.cx, self.cy)
                    self.center.append(tup)

        if Display:
            cv2.imshow(('Tag Tracking '+self.source.name),self.countourDisplay)
            #cv2.imshow(('Threshold '+self.source.name),self.thresh)

        self.result = self.sort(self.center)

        return self.result

   
    # sort() guarentees that the center(a, b) is such that a is the left tag coord
    #  and that the b is the right tag coord. We assume that there is only 2 tags
    #  and that the two tags are distinguishable by left and right. 
    
    # TO DO: create visual output debug
    def sort(self, inputList): 
        listofHorizontalCoords =[] # to store the x coords of the center coords
        if inputList != []: 
            print inputList[0][1]
            for center in inputList: # there are only two coords in center because we assume there are only 2 tags
                # the second coord is (under current camera config) the horizontal coord
                listofHorizontalCoords.append(inputList[inputList.index(center)][1]) 

            # find the max and min of the horizontal coords. The min is the left coord, max is the right. 
            LeftIndx = listofHorizontalCoords.index(max(listofHorizontalCoords))
            RightIndx = listofHorizontalCoords.index(min(listofHorizontalCoords))
            sortedList = [inputList[LeftIndx],inputList[RightIndx]]
            
            return sortedList
        else:
            return None


class StereoTracking:
    def __init__(self, sourcetop, sourcebot):
        self.sourcetop = sourcetop
        self.sourcebot = sourcebot

        #create tagTracking objects for both cameras
        self.AnalyzerBot = tagTracking(self.sourcebot) # Init bot processing
        self.AnalyzerTop = tagTracking(self.sourcetop) # Init right processing

        # Create trackbard to allow us to tune thresholding
        cv2.namedWindow('trackbars')
        cv2.createTrackbar('Thresh', 'trackbars', 180, 255, nothing)
        threshVal = cv2.getTrackbarPos('Thresh','trackbars')

        self.ColorList = [(255,0,0),(0,0,255)]
        self.plotMarker = ['g','m']

        #self.AnalyzerTop.calibrate(threshVal)
        #self.AnalyzerBot.calibrate(threshVal)

        self.baseline = 10.5 #Dimension, in inches, of the camera baseline
        self.XGuess = None
        self.YGuess = None

        self.Display = False #Can be set to true externally for debug

        self.state = 'waiting'

        self.savedCoord = [(),()]
        self.lastCoord = [(),()]

        plt.clf()
        plt.ylabel('Displacement')
        plt.xlabel('Time (ms)')

    def StereoUpdate(self, debug=False):

        self.sourcetop.update(Display = False)
        self.sourcebot.update(Display = False)

        #check if user has changed the threshold value using the sliding bar
        threshVal = cv2.getTrackbarPos('Thresh','trackbars')

        # positionBotArray and positionTopArray are arrays of xy tag centers by color
        # the tag color array order is: [blue, orange, green, maroon]

        positionTopArray = self.AnalyzerTop.tracking(threshVal, Display = self.Display)
        positionBotArray = self.AnalyzerBot.tracking(threshVal, Display = self.Display)

        #print "positionTopArray:", positionTopArray # Prints the xy coords of the tags
        #print "positionBotArray", positionBotArray

        if positionBotArray and positionTopArray:

            for i in range(2):

                positionBot = positionBotArray[i]
                positionTop = positionTopArray[i]
                #print "right pos:", positionTop, "left pos:", positionBot
                if positionBot and positionTop:
                    #print "Position top:", positionTop, "positionBot", positionBot
                    #while cv2.waitKey(15) < 0: pass
                    diff = (positionBot[0]-positionTop[0])
                    #depthMaybe = (12.0/diff)*1249.2307692  or *1380.5714286
                    depthMaybe = (self.baseline/diff)*1656.6857143
                    chordLength = depthMaybe*0.833378 #From rad*2*sin(theta/2)


                    XpercentAcrossBot = float(positionBot[0])/self.sourcebot.width
                    XpercentAcrossTop = float(positionTop[0])/self.sourcetop.width

                    XchordProjectionBot = XpercentAcrossBot*chordLength
                    XchordProjectionTop = XpercentAcrossTop*chordLength

                    XcenterProjectionBot = XchordProjectionBot - chordLength*.5
                    XcenterProjectionTop = XchordProjectionTop - chordLength*.5

                    XguessBot = XcenterProjectionBot-.5*self.baseline #Adjusts each guess to middle of baseline
                    XguessTop = XcenterProjectionTop+.5*self.baseline

                    ### NOW FOR Y

                    YpercentAcrossBot = float(positionBot[1])/self.sourcebot.height
                    YpercentAcrossTop = float(positionTop[1])/self.sourcetop.height

                    YchordProjectionBot = YpercentAcrossBot*chordLength
                    YchordProjectionTop = YpercentAcrossTop*chordLength

                    YcenterProjectionBot = YchordProjectionBot - chordLength*.5
                    YcenterProjectionTop = YchordProjectionTop - chordLength*.5

                    ### Compose coordinates
                    self.YGuess = (XguessBot+XguessTop)*.5
                    self.XGuess = (-YcenterProjectionBot-YcenterProjectionTop)*.5
                    self.Coord = (self.XGuess,self.YGuess,depthMaybe)

                    if debug:
                        print "----------------------------"
                        print "Bot:  {0}".format(positionBot)
                        print "Top: {0}".format(positionTop)
                        print "\nY disparity: {0}".format(positionTop[1]-positionBot[1])
                        print "X DISPARITY: {0}".format(diff)
                        print "\nDepth, Homogeneous: {0}".format(depthMaybe)
                        print "\nChord length: {0}".format(chordLength)
                        print "\nPec Across Bot: {0}".format(XpercentAcrossBot)
                        print "Pec Across Top: {0}".format(XpercentAcrossTop)
                        print "\nCenter Projection Bot: {0}".format(XcenterProjectionBot)
                        print "Center Projection Top: {0}".format(XcenterProjectionTop)
                        print "\nX Guess Bot: {0}".format(XguessBot)
                        print "X Guess Top: {0}".format(XguessTop)
                        print "\nX Guess : {0}".format(self.XGuess)
                        print "\nY Guess : {0}".format(self.YGuess)
                        print "\n\nCoordinate: ({0},{1},{2})".format(self.XGuess,self.YGuess,depthMaybe)

                    if self.state == 'waiting':
                        print "\nPosition of {0} : {1}".format(self.ColorList[i], (self.Coord) )
                        self.savedCoord[i] = self.Coord # Continuously update
                        self.lastCoord[i] = self.Coord
                        if self.savedCoord[0] and self.savedCoord[1]:
                            self.state = 'tracking'
                            self.startTime = time.time()
                    if self.state == 'tracking':
                        self.lastCoord[i] = self.Coord
                        print type(self.Coord)
                        plt.scatter((time.time()-(self.startTime)),(np.linalg.norm(np.asarray(self.Coord)-np.asarray(self.savedCoord[1]))),c=self.plotMarker[i])
                        plt.draw()
                        plt.pause(.000001)





                    # else:
                    #     print "\n\nDisplacement of {0} : {1}".format(self.AnalyzerBot.colorName[i],tuple(np.subtract(self.Coord, self.savedCoord[i])))
                    #     print 'hi'
                else:
                    if debug:
                        print "Object not detected in both frames"
