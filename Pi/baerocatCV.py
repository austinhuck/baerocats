# -*- coding: utf-8 -*-
    
##############################################################################
#   Import Necessary Packages
##############################################################################

from fractions import Fraction
import numpy as np
import cv2,time,os
from picamera.array import PiRGBArray
from picamera import PiCamera
from picamera import exc
from Logger import Log

#Set timeout for image check
PiCamera.CAPTURE_TIMEOUT = 5

##############################################################################
#   Define Baerocat Computer Vision Functions
##############################################################################

class Imaging:
    def __init__(self,Log):
        #Camera Characteristics
        self.xResolution = 3280
        self.yResolution = 2464
        self.framerate = 14
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
        self.t0 = Log.t0
        self.Cancel = False #Used to cancel imaging
        self.imgExtension = '.jpg'
        self.launchPath = Log.launchPath #launch directory path
        self.imgPath = Log.imgPath #raw image path
        self.processedPath = Log.processedPath #processed image path
        self.XTargetSize = 40 #feet
        self.YTargetSize = 40 #feet
        self.imageSuccess = 0
        self.imageIndex = 1

    def Initialize(self,attemptLimit):
    #Set conditions for initialization
        attemptLimit += 1 #add one because of python indexing
        cameraStarted = False
        attempt = 1
        self.camera = None
        
        #attempt initialization until conditions are met
        while cameraStarted == False and attempt < attemptLimit:
            try:
                Log.Log('Camera Initialization - Attempt '+str(attempt))
                self.camera = PiCamera() 
                self.cameraSettings() #set camera settings
                
                #Triggers when camera intialization is successful
                cameraStarted = True 
                Log.Log('Camera Successfully Initialized')
                self.Cancel = False

            except exc.mmal_check as e: #MMAL Errors typically raised when issue with connection
                template = 'PiCamera MMAL Error \n\t An exception of type {0} occurred. \n\tArguments:{1!r}'
                message = template.format(type(e).__name__, e.args)
                Log.Log(str(message))
                
            except exc.PiCameraClosed as e: #if operation is performed with closed camera object
                Log.Log(str(message))
                
            except Exception as e:
                template = 'PiCamera Exception of type {0} occurred. Arguments:\n\t{1!r}'
                message = template.format(type(e).__name__, e.args)
                Log.Log(str(message))
                
            finally:
                time.sleep(1)
                attempt += 1

        
        #End of check - report to log the results
        if attempt == attemptLimit:
            Log.Log('Stopped trying to initialize camera')
            self.Cancel = True
    
    def Reinitialize(self, attemptLimit):
        attemptLimit += 1 #add one because of python indexing
        cameraStarted = False
        attempt = 1
        self.camera = None
        
        #attempt initialization until conditions are met
        while cameraStarted == False and attempt < attemptLimit:
        
            Log.Log('Camera Reinitialization - Attempt '+str(attempt))
            try:
                self.CameraShutdown()
                print 'camera shutdown'
                self.camera = PiCamera() 
                print 'camera opened back up'
                self.cameraSettings() #set camera settings
                
                #Triggers when camera intialization is successful
                cameraStarted = True 
                Log.Log('Camera Successfully Initialized')
                self.Cancel = False

            except exc.mmal_check as e: #MMAL Errors typically raised when issue with connection
                template = 'PiCamera MMAL Error \n\t An exception of type {0} occurred. \n\tArguments:{1!r}'
                message = template.format(type(e).__name__, e.args)
                Log.Log(str(message))
                
            except exc.PiCameraClosed as e: #if operation is performed with closed camera object
                Log.Log(str(message))
                
            except Exception as e:
                template = 'PiCamera Exception of type {0} occurred. Arguments:\n\t{1!r}'
                message = template.format(type(e).__name__, e.args)
                Log.Log(str(message))
                
            finally:
                time.sleep(1)
                attempt += 1

        #End of check - report to log the results
        if attempt == attemptLimit:
            Log.Log('Stopped trying to reinitialize camera')
            self.Cancel = True
            
            
    def CameraCheck(self):
        #Use this during sensor check phase of program
        try: 
            cam = PiCamera()
            cam.close()
            Log.Log('Camera connected')
            return True
        except Exception:
            Log.Log('Camera not connected')
            return False
            
    
    #Define camera settings and attributes function
    def cameraSettings(self):
        Log.Log('Camera Warming Up and Setting Settings')
        
        self.camera.resolution = (self.xResolution, self.yResolution) 
        #self.camera.resolution = (self.xResolution/2, self.yResolution/2)
        self.camera.framerate = self.framerate
        time.sleep(1)
                
        #CAMERA SETTINGS
        self.camera.iso = 100 #guessing this will be good for indoors testing
        time.sleep(2) #allow camera to warm up

        self.camera.shutter_speed = self.camera.exposure_speed
        self.camera.exposure_mode = 'off'
        g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g
        
        #self.camera.brightness = 50
        #self.camera.flash_mode = 'off'
        self.camera.hflip = True
        self.camera.vflip = True
        self.camera.raw_format = 'bgr'
        #self.camera.video_stabilization = False
        
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
        f.write('Camera Shutter Speed:   ,'+str(self.camera.shutter_speed)+'\n')
        
        f.write('\n********Camera Mode Settings\n')
        f.write('Image Horizontal Flip:   ,'+str(self.camera.hflip)+'\n')
        f.write('Image Vertical Flip:   ,'+str(self.camera.vflip)+'\n')
        f.write('Camera Exposure Mode:   ,'+str(self.camera.exposure_mode)+'\n')
        f.write('Camera Sensor Mode:   ,'+str(self.camera.sensor_mode)+'\n')
        f.write('Camera Flash Mode:   ,'+str(self.camera.flash_mode)+'\n')
        f.write('Camera Raw Format:   ,'+str(self.camera.raw_format)+'\n')
        f.write('Camera Meter Mode:   ,'+str(self.camera.meter_mode)+'\n')
        f.write('Camera Video Stabilization:   ,'+str(self.camera.video_stabilization)+'\n')
        f.write('Image Denoise:   ,'+str(self.camera.image_denoise)+'\n')
        f.write('Camera Timeout (secs):   ,'+str(self.camera.CAPTURE_TIMEOUT)+'\n')
        f.close()
    
    
        
    #Define function for capturing image data
    def imgCapture(self):
        #for list of Picamera exceptions go here
        #http://picamera.readthedocs.io/en/release-1.10/_modules/picamera/exc.html

        Log.Log(str('Image %d' % self.imageIndex))
        try:
            #String to logs
            Log.Log(str('    Trying to capture Image %d' % self.imageIndex))
            
            #Set Filename and Take image
            filename = os.path.join(self.imgPath,'image'+str(self.imageIndex)+'-'+str('%0.6f'%self.tImage)+self.imgExtension)
            self.camera.capture(filename, use_video_port = True)
            
            #String to logs
            Log.Log(str('    Image %d Successfully Captured' % self.imageIndex))
            self.imageSuccess += 1
        except Exception as e:
            #String to logs
            Log.Log(str('    Image %d Failed: \n\t' % self.imageIndex)+str(e))
            
            self.Cancel = True #Try to initiate again if this is true
        finally:
            self.imageIndex += 1 #iterate image index
        
        #Attempt to reinitialize the camera      
        if self.Cancel == True:
            Log.Log('Attempting to Reinitialize Camera')
            #self.Reinitialize(10)

            
    #Baerocats designed CV program, 3 colors
    def imgProcess(self,img,alt):
        if img is not None:
            #Convert to HSV Space
            imgHSV = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) 

            #Threshold the HSV image to get three colors
            mask1 = cv2.inRange(imgHSV, self.lower_red, self.upper_red)
            mask2 = cv2.inRange(imgHSV, self.lower_blue, self.upper_blue)
            mask3 = cv2.inRange(imgHSV, self.lower_yellow, self.upper_yellow)

            #Create Image for output
            processed = img
         
            #Moment Calculations
            dmp1,contour1,hierarchy1 = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            dmp2,contour2,hierarchy2 = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            dmp3,contour3,hierarchy3 = cv2.findContours(mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contourList = [contour1,contour2,contour3]
            
            #Loop through contours
            for i,color in enumerate(['red','blue','yellow']):
                
                #Check to see if there are contours
                if len(contourList[i]) > 0:
                    for c in contourList[i][0]:
                        M = cv2.moments(c)
                        #if M["m00"] > area-areaSlop:
                        if M["m00"] > 30:
                            Log.ImageLog('        '+color+':   '+str(M["m00"]))
                            cX = int(M["m10"] / M["m00"]) #centroid x coordinate
                            cY = int(M["m01"] / M["m00"]) #centroid y coordinate
                            
                            # draw the contour and center of the shape on the images
                            cv2.drawContours(processed, [c], -1, (0, 255, 0), 3)
                            cv2.circle(processed, (cX, cY), 7, (255, 255, 255), -1)
                            cv2.putText(processed, color, (cX - 20, cY - 20),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                else: 
                    #This executes if no contours are found for a given color
                    Log.ImageLog('        No %s contours found'%color)
            
            return processed
        
        #If the image array is NoneType
        else:
            Log.ImageLog('        Image file is blank')

        
    #Function estimates area of expected target at given altitude,resolution            
    def estimateArea(self,alt):
        #Expected target dimensions based on FOV, height, resolution in feet
        xSize = alt*np.tan(self.xFOV/2*3.141/180)*2 #in feet
        ySize = alt*np.tan(self.yFOV/2*3.141/180)*2 #in feet
        
        #Expected pixel size based off resolution
        xPixel = self.XTargetSize/xSize*self.xResolution
        yPixel = self.YTargetSize/ySize*self.yResolution
        
        #Calculate area and return
        area = xPixel * yPixel
        return area

        
    #Define function for saving images
    def imgSave(self,img,imgType):
        if imgType == 'raw':
            #save raw img array to file
            imgFile = self.imgPath + '/image' + str(self.imageIndex) + '-' + str('%.6f' % self.tImage)+ self.imgExtension
        elif imgType == 'processed':
            #save processed image array to file
            imgFile = self.processedPath + '/image' + str(self.imageIndex) + '-' + str('%.6f' % self.tImage)+ '_processed'+self.imgExtension
        
        #Save image with filename made above
        cv2.imwrite(imgFile,img)

        
    #Geolocation Function
    def Geolocate(self):
        #Geolocation calculations
        
        #Log Geolocation Data
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
    def DescentImaging(self,alt):
        if self.Cancel == False:
            self.tImage = time.time()-self.t0 #get time

            #Save Data to Data File
            data = str(self.imageIndex)+', '+str('%.6f' % self.tImage)+', '+str(alt)
            
            Log.ImageData(data)
            
            #Capture raw image
            self.imgCapture()


    def ProcessAll(self,path):
        Log.Log('Attempting to process images')
        try:
            for file in os.listdir(path):
                if file.endswith(self.imgExtension):
                    Log.ImageLog('Processing '+file)
                    #Process Image
                    img = cv2.imread(os.path.join(path,file),1) 
                    
                    #Get time stamp from image name
                    timePart = file.split('-')[1].split('.')
                    timeStamp = str(timePart[0]+'.'+timePart[1])
                    self.tImage = float(timeStamp)
                    
                    #Get altitude from image log using timestamp
                    with open(Log.ImageDataFile) as f:
                        next(f)
                        for line in f:
                            rec = line.strip()
                            if rec.split(', ')[1] == timeStamp:
                                alt = float(rec.split(', ')[2])
                                
                                #set image index for processed file name
                                self.imageIndex = int(float(rec.split(', ')[0]))
                    
                    #Process Image
                    processed = self.imgProcess(img,alt)
                    
                    #Save Processed Image
                    self.imgSave(processed,'processed')
                    Log.Log(file+'  was processed and saved')
            
            #Log message
            Log.Log('Processed all available image files')
        
        except Exception as e:
            Log.Log('An error occurred while processing:\n\t' + str(e))
        
    
    #Closes down camera object 
    def CameraShutdown(self):
        #Try to shutdown camera object
        try:
            self.camera.close()
            Log.Log('Shutting down camera')
        except AttributeError:
            Log.Log('Tried shutting down camera object, but it doesnt exist')
        except Exception as e:
            Log.Log('Exception occurred when shutting down camera\n\t'+str(e))
    
##############################################################################
#               Proper Usage
##############################################################################        
'''
#create instance of baerocatCV
from Logger import Log
baerocatCV = Imaging(Log)

#When imaging is wanted
baerocatCV.Initialize(20)

#See if camera is initialized correctly, then continue
if baerocatCV.Cancel == False:
    with baerocatCV.camera:
        for x in xrange(5):
            #alt = TDC.GetAltitude()-alt0 #altitude - Z
            alt = 600+x*10 - 300
            
            #Check to see if cancelled again
            if baerocatCV.Cancel == False:
                baerocatCV.DescentImaging(alt)
            else:
                Log.Log('Imaging cancelled : Connection Lost \n\t Couldnt Reconnect')
                break
        
        Log.Log('Image Capture Phase Complete:\n\t \
            Altitude of %d has been reached \n\t \
            %d successful images captured' %(200,baerocatCV.imageSuccess))
else:
    Log.Log('Imaging cancelled because of failure to initiate')

#After Landing
baerocatCV.CameraShutdown()

#baerocatCV.ProcessAll(baerocatCV.imgPath)
'''

#####################################################################
#          Correct implementation of baerocatCV below
#####################################################################
'''
######################################
#     *******Ground Phase
######################################
#create instance of baerocatCV
from Logger import Log
baerocatCV = Imaging(Log)

######################################
# *******Flight Phase
######################################
#When imaging is wanted
baerocatCV.Initialize(30) #Try to initilialize for 30 attempts - ~30 seconds

#See if camera is initialized correctly, then continue
if baerocatCV.Cancel == False:
    with baerocatCV.camera:
        Get one data point to check altitude
        alt = TDC.GetAltitude()-alt0 #altitude - Z
        
        #Descent Imaging Phase
        while alt > 200:
            alt = TDC.GetAltitude()-alt0 #altitude - Z
            
            baerocatCV.DescentImaging(alt)
            #Check to see if cancelled due to connection loss
            if baerocatCV.Cancel == False:
                baerocatCV.DescentImaging(alt)
            else:
                Log.Log('Imaging cancelled : Connection Lost \n\t Couldnt Reconnect')
                break
        
        #Log that imaging is complete
        Log.Log('Image Capture Phase Complete:\n\t \
            Altitude of %d has been reached \n\t \
            %d successful images captured' %(200,baerocatCV.imageSuccess))        
    else:
        Log.Log('Imaging cancelled due to failure to initiate')

######################################
# *******Post Landing Phase
######################################
#Shutdown the camera
baerocatCV.CameraShutdown()

#Do something with the LED before processing
#THIS MEANS TRIPOD IS STILL FUNCTIONING AND SHOULD NOT BE SHUT OFF 
#COMMAND

#Process images
baerocatCV.ProcessAll(baerocatCV.imgPath)

#Do something with LED after processing - signals end of launch
#This means the TRIPOD can be shutdown
#COMMAND
'''
