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

##############################################################################
# Import the Python Packages - Subject to Change
##############################################################################
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
    #set flashing rates for LEDS
    rate1 = 1.5 #flashes per second
    t1 = 1/rate1

    #how many times to repeat flash cycle per check
    repeat = 2

    if systemGood == 1:
        GPIO.output(ledPin,GPIO.HIGH)
    else:
        for x in xrange(repeat):
            GPIO.output(ledPin,GPIO.HIGH)
            time.sleep(t1)
            GPIO.output(ledPin,GPIO.LOW)
            time.sleep(t1)

def LightTest(setting,pin,num,integrationTime):
    Log.Log('IntegrationTime(sec):' + str(integrationTime))
    TDC._tsl.set_integration_time(integrationTime) #DOUBLE CHECK THIS 
    count = 0
    if setting == 'switch':
        while getSwitch(pin) == True:
            Log.Log('Measurement'+str(count)+','+str(tdc.GetLightLevel()))
            count += 1
    elif setting == 'fixed':
        while count < num:
            Log.Log('Measurement'+str(count)+','+str(tdc.GetLightLevel()))
            count += 1
    Log.Log('**************************************')
    Log.Log(' ')
    Log.Log(' ')

##############################################################################
#####       This is the program that runs once the script starts         #####
##############################################################################

######################################  
#-------> USER INPUTS
#####################################

mode = 'test'

#Define GPIO Pins
startupSwitchGpio = 17 #Activation Switch GPIO pin 1
inRocketSwitchGpio = 22 #Put-TRIPOD-in-Rocket Switch GPIO pin 1
ledGpio = 24 #System Check GPIO Pin
servoActuateGpio = 26 #Servo actuation pin
servoSwitchGpio = 27 #Servo switch pin

######################################  
#-------> Ground Phase 0: Wait for Permission to Start
######################################

#Set up GPIO Pins for switches, LEDs, and servos
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(startupSwitchGpio, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(servoSwitchGpio, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(inRocketSwitchGpio, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(ledGpio,GPIO.OUT)

#First wait for main switch to signal to TRIPOD to start the rest of program
while getSwitch(startupSwitchGpio) == False:
    debugLED(ledGpio,0) #Light LED to Show Sensor Check beginning

print('Waiting for Activation Switch (GPIO 17)')

######################################  
#-------> Ground Phase 1: Start up
######################################
    
#Make launch directory and flight log file    
from Logger import Log
t0 = Log.t0 #Get initial time for timing everything
from baerocatCV import Imaging

#Create a Flight Log file for logging information about flight phases
Log.Log('Ground Phase 1: Start Up') #report to flight log

#Initialize the TDC and Radio
tdc = TDC.TDC()
tdc.Initialize()

debugLED(ledGpio,1) #Light LED to Show Sensor Check beginning

while getSwitch(inRocketSwitchGpio) == False:
    time.sleep(0)

######################################  
#-------> Ground Phase 1: Test Light Sensor
######################################    
pin = inRocketSwitchGpio
setting = 'fixed' #switch
num = 20

integrationTime = 0.402
LightTest(setting, pin, num, integrationTime)
    
integrationTime = 0.2
LightTest(setting, pin, num*2, integrationTime)
    
integrationTime = 0.1
LightTest(setting, pin, num*4, integrationTime)

integrationTime = 0.05
LightTest(setting, pin, num*8, integrationTime)

######################################
# -------> End of Program
######################################
Log.Log('End of Lighting Test') #report to flight log 
tdc.Stop() #Shutdown TDC
GPIO.cleanup() #cleanup GPIO


