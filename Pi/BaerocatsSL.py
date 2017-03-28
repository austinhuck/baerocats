# -*- coding: utf-8 -*-

##This code serves to develop the python packages for the first full scale test 
##on November 19, 2016.
##
##Revision Log: 
##    Date: 11/6/2016 - Brandon
##    Changes: Started programming and planning
##    
##    Date: 11/16/2016 - Brandon
##    Changes: Added in code for light sensor, continued editing flight program
##
##    Date: 11/18/2016 - Brandon
##    Changes: Added in code for Power on Test and Payload
##    
##    Date: 1/13/2017 - Brandon
##    Changes: Integration with Justas for January Launch
##    
##    Date: 1/18/2017 - Brandon
##    Changes: Integration with team for January 21
##
##    Date: 1/212017 - AJohnson
##    Changes: Added landing detection code
##    
##    Date: 03/05/2017 -AJohnson
##    Changes: exception handling for light sensor and landing detection code
##
##############################################################################
# Import the Python Packages - Subject to Change
##############################################################################
import cv2
import time, os, sys
import numpy as np
import RPi.GPIO as GPIO

##############################################################################
# Import Baerocat Custom Software
##############################################################################

import TDC
import Transmitting
import ServoControl

##############################################################################
#   Sensor and System Check functions
##############################################################################

#Function that checks switch position
def getSwitch(switchPin):
    #Check to see if outPin gets voltage
    return (GPIO.input(switchPin) == GPIO.HIGH)    

#This functions is used for lighting LEDs during debug check
def debugLED(ledPin, systemGood):
    if systemGood == 1:
        GPIO.output(ledPin,GPIO.HIGH)
    else:
        GPIO.output(ledPin,GPIO.LOW)

def flashLedAbort(ledPin):
    Log.Log('Fatal Error: Disable startup switch to exit.')
    last = True
    while getSwitch(startupSwitchGpio) == True:
        if last:
            GPIO.output(ledPin, GPIO.HIGH)
        else:
            GPIO.output(ledPin, GPIO.LOW)
        last = not last
        time.sleep(0.05)
    sys.exit()
            
def Landing(WThresh,DescRateThresh,BlockSize,SampleRate,ledGPIO):
    #Averages descent rate and IMU angular velocities over a block of BlockSize samples 
    #waits for them to fall within the specified thresholds that qualify landing

    #initialize variables...
    Landing=0
    W=np.zeros(BlockSize)
    DescRate=np.zeros(BlockSize)
    PauseTime=float(1)/float(SampleRate)
    block = 0

    #initial sample...
    wx,wy,wz=tdc.GetRotationRate()
    w0=(wx**2+wy**2+wz**2)**0.5 #angular velocity of TRIPOD
    t0=time.time()
    Alt0=tdc.GetAltitude()
    flasher=0
    for count in range(0,BlockSize):
        if count<BlockSize-1: #if block is not filled, keep taking data for current block
            if flasher==0:
                flasher=1
                debugLED(ledGPIO,0)
            elif flasher==1:
                flasher=0
                debugLED(ledGPIO,1)
            time.sleep(PauseTime) #sleep for dt
            #Sample data...
            wx,wy,wz=tdc.GetRotationRate()
            w1=(wx**2+wy**2+wz**2)**0.5 #angular velocity of TRIPOD
            t1=time.time()
            Alt1=tdc.GetAltitude()
            dt=(t0-t1)
            DescRate[count]=(Alt1-Alt0)/dt #descent rate of TRIPOD over dt
            W[count]=(w0+w1)/2 #average angular velocity over dt
            w0=w1
            t0=t1
            Alt0=Alt1
            print 'Altitude: ',Alt1,'Angular Velocity: ',w1,'BlockNumber: ',str(count)
        else: #block is filled: average data over block
            wAvg=sum(W)/len(W)
            DescRateAvg=sum(DescRate)/len(DescRate)
            if wAvg<WThresh and abs(DescRateAvg)<DescRateThresh:
                Landing=1
            block=block+1
            Log.Log('        Checking movement average:')
            Log.Log('        RotationRateAverage,'+str(wAvg)+',DescentRateAverage,'+str(DescRateAvg))
    return Landing

##############################################################################
#####       This is the program that runs once the script starts         #####
##############################################################################

######################################  
#-------> USER INPUTS
#####################################

mode = 'test'
#mode = 'launch'

#Define GPIO Pins
startupSwitchGpio = 22 #Activation Switch GPIO pin 1
inRocketSwitchGpio = 17 #Put-TRIPOD-in-Rocket Switch GPIO pin 1
ledGPIO = 12 #24 #System Check GPIO Pin
servoActuateGpio = 18 #Servo actuation pin
servoSwitchGpio = 27 #Servo switch pin

#Landing detection settings:
WThresh = 0.05 #rad/s
DescRateThresh = 5 #ft/s
BlockSize = 10 #number of samples to average
SampleRate = 2 #Hz

######################################  
#-------> Ground Phase 0: Wait for Permission to Start
######################################

#Set up GPIO Pins for switches, LEDs, and servos
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(startupSwitchGpio, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(servoSwitchGpio, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(inRocketSwitchGpio, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(ledGPIO,GPIO.OUT)

print('Waiting for Activation Switch (GPIO 17)')

#First wait for main switch to signal to TRIPOD to start the rest of program
flasher=1
while getSwitch(startupSwitchGpio) == False:
    #flash led until start-up switch
    if flasher==0:
        flasher=1
        debugLED(ledGPIO,0)
    elif flasher==1:
        flasher=0
        debugLED(ledGPIO,1)
    time.sleep(0.5)
######################################  
#-------> Ground Phase 1: Start up
######################################
    
#Make launch directory and flight log file    
from Logger import Log
t0 = Log.t0 #Get initial time for timing everything
Log.Log(str(Log.imgPath)+str(Log.processedPath))
from BaerocatsCV import Imaging

#Create a Flight Log file for logging information about flight phases
Log.Log('Ground Phase 1: Start Up') #report to flight log

#Initialize the TDC and Radio
tdc = TDC.TDC()
radio = Transmitting.Radio()

try:
    tdc.Initialize()
    radio.Initialize()
except Exception as e:
    Log.Log(str(e))
    flashLedAbort(ledGPIO)

######################################  
#-------> Ground Phase 2: System Sensor Check
######################################
Log.Log('Ground Phase 2: System Sensor Check') #report to flight log

#Log that sensors pass check
Log.Log('Sensors pass system check')

######################################  
#-------> Ground Phase 3: Set Up TRIPOD Legs
######################################
Log.Log('Ground Phase 3: Setting Up TRIPOD Legs') #report to flight log

# Debug LED in order to inform us when the code is running
debugLED(ledGPIO,1) 
Log.Log('Debug LED ignited')

#Servo Code
servo = ServoControl.ServoControl(servoSwitchGpio,servoActuateGpio)
time.sleep(0.5)

#Actuate servo based on switch input.
#Report servo status every second
while getSwitch(inRocketSwitchGpio) == False:

    if servo.IsServoOpen():
        Log.Log('Servo Open')
    else:
        Log.Log('Servo Closed')
    
    reps = 0
    while getSwitch(inRocketSwitchGpio) == False and reps < 10:
        servo.CheckServoSwitch()
        time.sleep(0.1)
        reps = reps + 1

Log.Log('TRIPOD Legs Set Up') #report to flight log    

######################################  
#-------> Ground Phase 4: Waiting to be placed in rocket
###################################### 
Log.Log('Ground Phase 4: Waiting to be placed in rocket') #report to flight log

time.sleep(1) #Small wait time for light sensing

#Define light sensor threshold for ON or OFF
tempLight = tdc.GetLightLevel()
while tempLight >= 30000: #loop until not saturated
     tempLight = tdc.GetLightLevel()
     debugLED(ledGPIO,0) #flash led until not saturated  
ambientLight = tempLight
debugLED(ledGPIO,1)

lightThreshold = ambientLight * 0.50 #this is a dummy value for now
Log.Log('Ambient Light Threshold Set, '+str(lightThreshold))

#Define ground altitude for descent altimeter cut off
alt0 = tdc.GetAltitude()
Log.Log('Ground Altitude Measured (feet), '+str(alt0))

#Wait to be put in the rocket
if mode == 'test':
    #flash LED to indicate LS threshold and altitude calibration success
    debugLED(ledGPIO,0)
    time.sleep(.5)
    debugLED(ledGPIO,1)
    time.sleep(.5)
    debugLED(ledGPIO,0)
    time.sleep(.5)
    debugLED(ledGPIO,1)
    time.sleep(.5)
    debugLED(ledGPIO,0)
    time.sleep(.5)
    debugLED(ledGPIO,1)
    time.sleep(.5)
    time.sleep(5) 
elif mode == 'launch':
    #flash LED to indicate LS threshold and altitude calibration success
    debugLED(ledGPIO,0)
    time.sleep(.5)
    debugLED(ledGPIO,1)
    time.sleep(.5)
    debugLED(ledGPIO,0)
    time.sleep(.5)
    debugLED(ledGPIO,1)
    time.sleep(.5)
    debugLED(ledGPIO,0)
    time.sleep(.5)
    debugLED(ledGPIO,1)
    time.sleep(.5)
    time.sleep(60)

######################################
#-------> Ground Phase 5: Waiting for launch on pad
######################################
Log.Log('Ground Phase 5: Waiting for launch on pad') #report to flight log

#Start the TDC module
tdc.Record(0)
Log.Log('TDC Module Started') 

######################################
# -------> Flight Phase 1: Ascent
######################################
Log.Log('Flight Phase 1: Ascent') #report to flight log

#Check for ejection from rocket
while tdc.GetLightLevel() < lightThreshold:
    time.sleep(1)

######################################   
# -------> Flight Phase 2: Separation
######################################  
Log.Log('Flight Phase 2: Separation Detected') #report to flight log

#Wait for 5 seconds after ejection, lets TRIPOD perturbations decay
time.sleep(5)

######################################  
# -------> Flight Phase 3: Faller-ing
######################################  
Log.Log('Flight Phase 3: Descent') #report to flight log

#Initialize camera to get capture settings
BaerocatsCV = Imaging(Log)


if mode == 'test':
    Log.Log('Test mode initiated.')
    BaerocatsCV.Initialize(10)
    if BaerocatsCV.Cancel == False:
        with BaerocatsCV.camera:
            for n in xrange(16):
                alt = tdc.GetAltitude()-alt0
                BaerocatsCV.DescentImaging(alt)         
    else:
        Log.Log('Imaging cancelled : Connection Lost \n\t Couldnt Reconnect')
elif mode == 'launch':
    Log.Log('Launch mode initiated.')
    BaerocatsCV.Initialize(30)
    DescentTime0=time.time()
    DescentTime=0
    if BaerocatsCV.Cancel == False:
        with BaerocatsCV.camera:
            #Get one data point to check altitude
            alt = tdc.GetAltitude()-alt0 #altitude - Z
            
            #TEMPORARY ALTITUDE IGNORE
            #numPhotos = 0
            #Descent Imaging Phase
            while alt > 200 : #numPhotos < 75:   #
                alt = tdc.GetAltitude()-alt0 #altitude - Z
                DescentTime = time.time()-DescentTime0
                Log.Log('Descent Time : ' + str(DescentTime) + 'Seconds')
                #numPhotos = numPhotos + 1
                #BaerocatsCV.DescentImaging(alt)
                #Check to see if cancelled due to connection loss
                if BaerocatsCV.Cancel == False:
                    BaerocatsCV.DescentImaging(alt)
                else:
                    Log.Log('Imaging cancelled : Connection Lost \n\t Couldnt Reconnect')
                    break
            
            #Log that imaging is complete
            Log.Log('Image Capture Phase Complete:\n\t \
                Altitude of %d has been reached \n\t \
                %d successful images captured' %(200,BaerocatsCV.imageSuccess))        
    else:
        Log.Log('Imaging cancelled due to failure to initiate')

#Shutdown the camera
BaerocatsCV.CameraShutdown()
  
######################################  
# -------> Flight Phase 4: Landering
###################################### 

Log.Log('Flight Phase 4: Landering') #report to flight log

#Landing Detection
while Landing(WThresh,DescRateThresh,BlockSize,SampleRate,ledGPIO) == 0:
    Log.Log('Checking for Landering')
    time.sleep(0)
debugLED(ledGPIO,1)

Log.Log('Landering Detected')    

######################################  
# -------> Flight Phase 5: Lander Upstandering
######################################  
Log.Log('Flight Phase 5: Fallen Lander Upstandering') #report to flight log

#Command leg servo to open
servo.LandServo()
Log.Log('Servo landing activated')

######################################  
# -------> Flight Phase 6: Fallen Upstanded Lander Bystandering
######################################
Log.Log('Flight Phase 6: Fallen Upstanded Lander Bystandering') #report to flight log

#Process images
BaerocatsCV.ProcessAll(BaerocatsCV.imgPath,ledGPIO)

#Do something with LED after processing - signals end of launch
#This means the TRIPOD can be shutdown
#COMMAND


# Perform Geolocation operation
#>>>>Weighted average function/calculation

#while loop keeps the TRIPOD transmitting until a switch is pressed
while getSwitch(startupSwitchGpio) == True:
    time.sleep(0.1)

######################################     
# -------> End of Program
######################################
Log.Log('End of launch, rest in pepperonis') #report to flight log 
tdc.Stop() #Shutdown TDC
radio.Shutdown() #Shutdown Radio
GPIO.cleanup() #cleanup GPIO
