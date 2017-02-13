# -*- coding: utf-8 -*-
    
##############################################################################
#   Import Necessary Packages
##############################################################################

from fractions import Fraction
import numpy as np
import cv2,time,os
from picamera.array import PiRGBArray
from picamera import PiCamera
from Logger import Log

##############################################################################
#   Define Baerocat Computer Vision Functions
##############################################################################

class Imaging:
    def __init__(self,Log):
        #Camera Characteristics
        self.xResolution = 3280
        self.yResolution = 2464
        self.framerate = 3
        self.cameraType = 'wide'
        if self.cameraType == 'wide':
            self.xFOV = 110 #degrees
            self.yFOV = 82.6 #degrees
        elif self.cameraType == 'normal':
            self.xFOV = 62.2 #degrees
            self.yFOV = 48.8 #degrees
            
        #Binary Mask Settings
        self.lower_red = np.array([160,100,100], dtype = "uint8")
        self.upper_red = np.array([180,255,255], dtype = "uint8")
        self.lower_blue = np.array([100,100,100], dtype = "uint8")
        self.upper_blue = np.array([120,255,255], dtype = "uint8")
        self.lower_yellow = np.array([15,100,100], dtype = "uint8")
        self.upper_yellow = np.array([35,255,255], dtype = "uint8")
        
        #Other
        self.tImage = 0
        self.launchPath = Log.launchPath #launch directory path
        self.imgPath = Log.imgPath #raw image path
        self.processedPath = Log.processedPath #processed image path
        self.XTargetSize = 40 #feet
        self.YTargetSize = 40 #feet
        self.imageIndex = 1

    def Initialize(self):
        self.camera = PiCamera()
        self.cameraSettings()
        self.rawCapture = PiRGBArray(self.camera)
        
    #Define camera settings and attributes function
    def cameraSettings(self):
        Log.Log('Camera Warming Up')
        
        self.camera.framerate = self.framerate
        self.camera.resolution = (self.xResolution, self.yResolution) 
        time.sleep(1)
                
        #CAMERA SETTINGS
        self.camera.iso = 400 #guessing this will be good for indoors testing
        time.sleep(2) #allow camera to warm up
        self.camera.shutter_speed = self.camera.exposure_speed
        self.camera.exposure_mode = 'off'
        g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g
        #self.camera.brightness = 50
        #self.camera.digital_gain =
        #self.camera.analog_gain = 
        #self.camera.exposure_speed =
        self.camera.flash_mode = 'off'
        self.camera.raw_format = 'bgr'
        self.camera.video_stabilization = False
        
        ########################################################
        #       Write Text File to store camera settings
        ########################################################
        f = open(os.path.join(self.launchPath,'cameraSettings.txt'),'wr')
        f.write('Camera Setting Document\n')
        f.write('Camera Resolution (w,h):   ,'+str(self.camera.resolution)+'\n')
        f.write('Camera Frame Rate (fps):   ,'+str(self.camera.framerate)+'\n')
        f.write('Camera ISO:   ,'+str(self.camera.iso)+'\n')
        f.write('Camera AWB Gains:   ,'+str(self.camera.awb_mode)+'\n')
        f.write('Camera Brightness:   ,'+str(self.camera.brightness)+'\n')
        f.write('Camera Digital Gain:   ,'+str(self.camera.digital_gain)+'\n')
        f.write('Camera Analog Gain:   ,'+str(self.camera.analog_gain)+'\n')
        f.write('Camera Exposure Speed:   ,'+str(self.camera.exposure_speed)+'\n')
        f.write('Camera Exposure Mode:   ,'+str(self.camera.exposure_mode)+'\n')
        f.write('Camera Shutter Speed:   ,'+str(self.camera.shutter_speed)+'\n')
        f.write('Camera Flash Mode:   ,'+str(self.camera.flash_mode)+'\n')
        f.write('Camera Raw Format:   ,'+str(self.camera.raw_format)+'\n')
        f.write('Camera Video Stabilization:   ,'+str(self.camera.video_stabilization)+'\n')
        f.close()

        
    #Define function for capturing image data
    def imgCapture(self):
        '''self.camera.capture(self.rawCapture, format='bgr', use_video_port = True)
        img = self.rawCapture.array
        self.rawCapture.truncate(0)'''
        
        self.camera.capture(os.path.join(self.imgPath,'image'+str(self.imageIndex)+'-'+str('%0.6f'%self.tImage)+'.jpg'), use_video_port = True)
        
        Log.ImageLog(str(str(self.tImage)+', Image %d Captured' % self.imageIndex)) #Log Image Capture
        self.imageIndex += 1
        #return img

        
    #Baerocats designed CV program, 3 colors
    def imgProcess(self,img,alt):
        #Convert to HSV Space
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 

        #Threshold the HSV image to get three colors
        mask1 = cv2.inRange(imgHSV, self.lower_red, self.upper_red)
        mask2 = cv2.inRange(imgHSV, self.lower_blue, self.upper_blue)
        mask3 = cv2.inRange(imgHSV, self.lower_yellow, self.upper_yellow)

        #Create Image for output
        processsed = img
     
        #Moment Calculations
        dmp1,contour1,hierarchy1 = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dmp2,contour2,hierarchy2 = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dmp3,contour3,hierarchy3 = cv2.findContours(mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #contour1 = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #contour2 = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #contour3 = cv2.findContours(mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contourList = [contour1,contour2,contour3]
        for i,color in enumerate(['red','blue','yellow']):
            for c in contourList[i][0]:
                M = cv2.moments(c)
                #if M["m00"] > area-areaSlop:
                if M["m00"] > 30:
                    Log.ImageLog('        '+color+':   '+str(M["m00"]))
                    cX = int(M["m10"] / M["m00"]) #centroid x coordinate
                    cY = int(M["m01"] / M["m00"]) #centroid y coordinate
                    
                    # draw the contour and center of the shape on the images
                    cv2.drawContours(processsed, [c], -1, (0, 255, 0), 3)
                    cv2.circle(processsed, (cX, cY), 7, (255, 255, 255), -1)
                    cv2.putText(processsed, color, (cX - 20, cY - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        return processed

        
    #Function estimates area of expected target at given altitude,resolution            
    def estimateArea(self,alt):
        #Expected target dimensions based on FOV, height, resolution in feet
        xSize = alt*np.tan(self.xFOV/2*3.141/180)*2 #in feet
        ySize = alt*np.tan(self.yFOV/2*3.141/180)*2 #in feet
        
        #Expected pixel size based off resolution
        xPixel = self.XTargetSize/xSize*self.xResolution
        yPixel = self.YTargetSize/ySize*self.yResolution
        
        area = xPixel * yPixel
        return area

        
    #Define function for saving images
    def imgSave(self,img,imgType):
        fileExtenstion = '.jpg'
        if imgType == 'raw':
            #save raw img array to file
            imgFile = self.imgPath + '/image' + str(self.imageIndex) + '-' + str('%.6f' % self.tImage)+ fileExtenstion
        elif imgType == 'processed':
            #save processed image array to file
            imgFile = self.imgPath + '/image' + str(self.imageIndex) + '-' + str('%.6f' % self.tImage)+ '_processed'+fileExtenstion
        cv2.imwrite(imgFile,img)

        
    #Geolocation Function
    def Geolocate(self):
        #Geolocation calculations
        
        #data = 
        Log.GeolocationData(str(self.tImage)+', '+str(self.imageIndex)+', '+str(altitude)+', '+str(latGPS)+', '+str(lonGPS))
    
    
    #Defines function that applies linear weighted average to GPS list
    def GeolocateWeightedAverage(self,aveType):
        #This program may or may not need to have section for importing data from file
        
        #Preallocate space for weights
        weights = np.zeros(latGPS.shape, dtype=float)
        sumAltitude = altitude.sum()
        
        #linear weighted average
        if aveType == 'linear':
            for num,alt in enumerate(altitude):
                weights[num] = 1-Fraction(alt,sumAltitude)
        #parabolic weighted average
        elif aveType == 'parabolic':
            for num,alt in enumerate(altitude):
                weights[num] = float(Fraction(alt,sumAltitude)**2)
        #cubic weighted average    
        elif aveType == 'cubic':
            for num,alt in enumerate(altitude):
                weights[num] = float(Fraction(alt,sumAltitude)**3)
        #logarithmic weighted average
        elif aveType == 'log':
            for num,alt in enumerate(altitude):
                weights[num] = np.log(float(Fraction(alt,sumAltitude)))
            
        weightingTotal = weights.sum()
        GPSWeights = np.divide(weights,weightingTotal)
            
        weightedLatitude = np.multiply(GPSWeights,latGPS).sum()
        weightedLongitude = np.multiply(GPSWeights,lonGPS).sum()   
        
        Log.Log('Weighted Average of GPS Coordinates Calculated\n')
        Log.Log('    Weighted Latitude:,'+str(weightedLatitude)+'\n')
        Log.Log('    Weighted Longitude:,'+str(weightedLongitude)+'\n')
        
    #Function to run during descent loop
    def DescentImaging(self,TDC):
        self.tImage = time.time()-Log.t0 #get time
        alt = TDC.GetAltitude()-alt0 #altitude - Z
        orientW,orientX,orientY,orientZ = TDC.GetOrientation() #get orientation vector
        latGPS,lonGPS = TDC.GetGPSPosition() #GPS - X,Y
        
        #Used for Testing - REPLACE
        '''
        orientW = 3 + self.imageIndex
        orientX = 2 + self.imageIndex
        orientY = 3 + self.imageIndex
        orientZ = 4 + self.imageIndex
        alt = 5 + self.imageIndex
        latGPS = 6 + self.imageIndex
        lonGPS = 7 + self.imageIndex
        '''
        
        #Save Data to Data File
        data = str(self.imageIndex)+', '+str('%.6f' % self.tImage)+', '+str(orientW)+', '+str(orientX)+ \
                ', '+str(orientY)+', '+str(orientZ)+', '+str(alt)+', '+str(latGPS)+', '+str(lonGPS)
        
        Log.ImageData(data)

        #Capture raw image
        self.imgCapture()

        #Save Raw Image
        #self.imgSave(raw,'raw')
        
        #Process Image
        #processed = self.imgProcess(img,alt)
        
        #Save Processed Image
        #self.imgSave(processed,'processed')
        
        #Geolocation Algorithm
        #TargetLat,TargetLon = self.Geolocate(self)

        
        
    #Closes down camera object and 
    def Shutdown(self):
        self.camera.close()

##############################################################################
#               Proper Usage
##############################################################################        
#create instance of baerocatCV
##from Logger import Log
##baerocatCV = Imaging(Log)
##baerocatCV.Initialize()

'''
try:
    baerocatCV.Initialize()
    with baerocatCV.camera:
        Log.Log('Imaging Started')
        for x in xrange(3):
            baerocatCV.DescentImaging()
finally:
    Log.Log('Imaging Complete')'''
