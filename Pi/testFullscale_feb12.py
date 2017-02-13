# -*- coding: utf-8 -*-
"""
This code serves to develop the python packages for the first full scale test 
on November 19, 2016.

Revision Log: 
    Date: 11/6/2016 - Brandon
    Changes: Started programming and planning
    
    Date: 11/16/2016 - Brandon
    Changes: Added in code for light sensor, continued editing flight program

    Date: 11/18/2016 - Brandon
    Changes: Added in code for Power on Test and Payload
    
    Date: 1/13/2017 - Brandon
    Changes: Integration with Justas for January Launch
    
    Date: 1/18/2017 - Brandon
    Changes: Integration with team for January 21

    Date: 1/212017 - AJohnson
    Changes: Added landing detection code
"""
##############################################################################
# Import the Python Packages - Subject to Change
##############################################################################
'''from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2'''
import time, os, sys
import numpy as np
import RPi.GPIO as GPIO

##############################################################################
# Import Baerocat Custom Software
##############################################################################

import TDC
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
    #set flashing rates for LEDS
    rate1 = 1.5 #flashes per second
    t1 = 1/rate1

    #how many times to repeat flash cycle per check
    repeat = 5

    if systemGood == 1:
        GPIO.output(ledPin,GPIO.HIGH)
    else:
        for x in xrange(repeat):
            GPIO.output(ledPin,GPIO.HIGH)
            time.sleep(t1)
            GPIO.output(ledPin,GPIO.LOW)
            time.sleep(t1)
            
def Landing(WThresh,DescRateThresh,BlockSize,SampleRate):
    #Averages descent rate and IMU angular velocities over a block of BlockSize samples 
    #waits for them to fall within the specified thresholds that qualify landing

    #initialize variables...
    Landing=0
    W=np.zeros(BlockSize)
    DescRate=np.zeros(BlockSize)
    PauseTime=1/SampleRate
    block = 0

    #initial sample...
    wx,wy,wz=tdc.GetRotationRate()
    w0=(wx**2+wy**2+wz**2)**0.5 #angular velocity of TRIPOD
    t0=time.time()
    Alt0=tdc.GetAltitude()

    for count in range(0,BlockSize):
        if count<BlockSize-1: #if block is not filled, keep taking data for current block
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
            print Alt1
            print(count)
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
#-------> Ground Phase 0: Wait for Permission to Start
###################################### 

#Define GPIO Pins
activationSwitchGpio = 17 #Activation Switch GPIO pin 1
inRocketSwitchGpio = 22 #Put-TRIPOD-in-Rocket Switch GPIO pin 1
ledGpio = 24 #System Check GPIO Pin
servoActuateGpio = 26 #Servo actuation pin
servoSwitchGpio = 27 #Servo switch pin

#Set up GPIO Pins for switches, LEDs, and servos
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(activationSwitchGpio, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(servoSwitchGpio, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(inRocketSwitchGpio, GPIO.IN, GPIO.PUD_DOWN)

GPIO.setup(ledGpio,GPIO.OUT)

print('Waiting for Activation Switch (GPIO 17)')

#First wait for main switch to signal to TRIPOD to start the rest of program
while getSwitch(activationSwitchGpio) == False:
    time.sleep(1)

######################################  
#-------> Ground Phase 1: Start up
######################################
    
#Make launch directory and flight log file    
from Logger import Log
t0 = Log.t0 #Get initial time for timing everything
from baerocatCV import Imaging

#Create a Flight Log file for logging information about flight phases
Log.Log('Ground Phase 1: Start Up') #report to flight log

#Initialize the TDC
tdc = TDC.TDC()
tdc.Initialize()

######################################  
#-------> Ground Phase 2: System Sensor Check
######################################
Log.Log('Ground Phase 2: System Sensor Check') #report to flight log

debugLED(ledGpio,1) #Light LED to Show Sensor Check beginning

'''
#Check sensors and system continuity
sns=Sensors.Sense()
ErrorArray=sns.Failed()

try: #check picamera for connection
    PiCamera()
except:
    ErrorArray.append('cam fail')
    pass

#Communnicate sensor errors to ground stationn
Log.Log('Sensor Failure:'+ErrorArray)

#Keep checking sensors
while len(ErrorArray)>0:
    #illuminate LEDs
    debugLED(ledGpio,0)
    time.sleep(5)
    
    #Clear Error Array
    ErrorArray = []
    
    #Check sensors again
    sns=Sensors.Sense()
    ErrorArray=sns.Failed()
    
    try: #check picamera
        PiCamera()
    except:
        ErrorArray.append('cam fail')
        pass
    
    #Send ErrorArray to ground station
    #>>>>>>TDC Diagnostic
'''
	
#Show system check as good
debugLED(ledGpio,1)

#Log that sensors pass check
Log.Log('Sensors pass system check')

######################################  
#-------> Ground Phase 3: Set Up TRIPOD Legs
######################################
Log.Log('Ground Phase 3: Setting Up TRIPOD Legs') #report to flight log

#Servo Code
servo = ServoControl.ServoControl(servoSwitchGpio,servoActuateGpio)
while getSwitch(inRocketSwitchGpio) == False:
    servo.checkServoSwitch()

Log.Log('TRIPOD Legs Set Up') #report to flight log    

######################################  
#-------> Ground Phase 4: Waiting to be placed in rocket
###################################### 
Log.Log('Ground Phase 4: Waiting to be placed in rocket') #report to flight log

time.sleep(1) #Small wait time for light sensing

#Define light sensor threshold for ON or OFF  
ambientLight = tdc.GetLightLevel()
lightThreshold = ambientLight * 0.50 #this is a dummy value for now
Log.Log('Ambient Light Threshold Set, '+str(lightThreshold))

#Define ground altitude for descent altimeter cut off
alt0 = tdc.GetAltitude()
Log.Log('Ground Altitude Measured (feet), '+str(alt0))

time.sleep(5) #Wait to be put in the rocket
#time.sleep(5*60) #Wait to be put in the rocket

######################################
#-------> Ground Phase 5: Waiting for launch on pad
######################################
Log.Log('Ground Phase 5: Waiting for launch on pad') #report to flight log

#Start the TDC module
tdc.Record(0)
Log.Log('TDC Module Started') 

#Orientation detection for Launch Pad Set Up Detection
#>>>>>>Orientation Detection Function/While Loop

# Launch detection code - optional later
#>>>>>>Launch Detection Code Function/While Loop

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
baerocatCV = Imaging(Log)
baerocatCV.Initialize()

with baerocatCV.camera:
    while tdc.GetAltitude()-alt0>200:
        baerocatCV.DescentImaging(tdc)
	
  
######################################  
# -------> Flight Phase 4: Landering
###################################### 
Log.Log('Flight Phase 4: Landering') #report to flight log

#Landing detection settings:
WThresh=0.001 #rad/s
DescRateThresh=5 #ft/s
BlockSize=10 #number of samples to average
SampleRate=5 #Hz

#Landing Detection
while Landing(WThresh,DescRateThresh,BlockSize,SampleRate) == 0:
    Log.Log('Checking for Landering')
    time.sleep(0)

Log.Log('Landering Detected')    

######################################  
# -------> Flight Phase 5: Lander Upstandering
######################################  
Log.Log('Flight Phase 5: Fallen Lander Upstandering') #report to flight log

#Command leg servo to open
servo.LandServo()

######################################  
# -------> Flight Phase 6: Fallen Upstanded Lander Bystandering
######################################
Log.Log('Flight Phase 6: Fallen Upstanded Lander Bystandering') #report to flight log

# Calculated weighted average of Geolocation Data
#>>>>Weighted average function/calculation

#while loop keeps the TRIPOD transmitting until a switch is pressed
while getSwitch(activationSwitchGpio) == True:
    time.sleep(5)

######################################     
# -------> End of Program
######################################
Log.Log('End of launch, rest in pepperonis') #report to flight log 
tdc.Stop() #Shutdown TDC
GPIO.cleanup() #cleanup GPIO
