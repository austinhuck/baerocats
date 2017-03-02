# pylint: disable=C0103, C0111, C1001

import os
import time

class logger:
    launchPath = ""
    imgPath = ""
    processedPath = ""
    logFile = ""
    ImagelogFile = ""
    t0 = ""
    phase = ""

    def __init__(self):
        self.launchPath, self.imgPath, self.processedPath = \
                         self.launchDirectory('/home/pi/Data')
        self.t0 = time.time()
        
        #Log File Set Up
        self.logFile = os.path.join(self.launchPath, 'Log.csv')
        flightLog = open(self.logFile, 'a+')
        flightLog.write('TIME(seconds), MESSAGE' + '\n')
        flightLog.close()
        
        #Image Data File Set Up
        self.ImageDataFile = os.path.join(self.launchPath, 'ImageData.csv')
        ImageData = open(self.ImageDataFile, 'a+')
        ImageData.write('Index,tImage,orientW,orientX,orientY,orientZ,alt,TRIPODlatitude,TRIPODlongitude\n')
        ImageData.close()
        
        #Image Log File Set Up - Used for reporting Processing Results
        self.ImageLogFile = os.path.join(self.launchPath, 'ImageLog.csv')
        ImageLog = open(self.ImageLogFile, 'a+')
        ImageLog.write('Below are the results of centroid areas that are processed\n')
        ImageLog.close()
		
		#Geolocation Log File Set Up
        self.GeolocationFile = os.path.join(self.launchPath, 'GeolocationData.csv')
        GeolocationData = open(self.GeolocationFile, 'a+')
        GeolocationData.write('Time,Index,Altitude,Latitude,Longitude\n')
        GeolocationData.close()

    #Get present working directory, and make files paths for data storage
    def launchDirectory(self, pwd):
        #launchDir = time.strftime('LAUNCH_%Y-%m-%d_%H-%M-%S')
        launchDir = time.strftime('LAUNCH_%Y-%b%d_%H-%M-%S%p')
        launchPath = os.path.join(pwd, launchDir)
        imgPath = os.path.join(launchPath, 'raw')
        processedPath = os.path.join(launchPath, 'processed')

        #make appropriate directories
        if not os.path.exists(launchPath):
            os.makedirs(launchPath) #directory to store all launch information
            os.makedirs(imgPath) #directory to store raw images
            os.makedirs(processedPath) #directory to store processed images

        return launchPath, imgPath, processedPath
    
    #Record to flight log file
    def Log(self, stringToLog):
        flightLog = open(self.logFile, 'a+')
        #content = str(time.time() - self.t0) + ', ' + stringToLog.replace(',', '')
        content = str(time.time() - self.t0) + ', ' + stringToLog
        flightLog.write(content + '\n')
        print(content)
        flightLog.close()
    
    #Record TRIPOD state data when image is captured to a file
    def ImageData(self, stringToLog):
        ImageData = open(self.ImageDataFile, 'a+')
        ImageData.write(stringToLog + '\n')
        ImageData.close()
        Log.Log('Image Data Recorded')
   
    #Record image processing results to a file
    def ImageLog(self, stringToLog):
        ImageLog = open(self.ImageLogFile, 'a+')
        ImageLog.write(stringToLog + '\n')
        ImageLog.close()
        print stringToLog
        Log.Log('Image Taken')

    #Record geolocation calculation results to a file
    def GeolocationData(self, stringToLog):
        GeolocationData = open(self.GeolocationFile, 'a+')
        GeolocationData.write(stringToLog + '\n')
        GeolocationData.close()
        Log.Log('Geolocation calculated')
    
    #Set phase of flight in logger
    def setPhase(self,phase):
        self.phase = phase
        self.Log(phase)
    
    #Return the phase of flight
    def getPhase(self):
        return self.phase

Log = logger()
