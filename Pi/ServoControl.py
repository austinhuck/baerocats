# pylint: disable=C0103, C0111, C1001, C0326

import RPi.GPIO as GPIO
import time
from Logger import Log

class ServoControl:
    #Switch is on pin 17
    #Servo is on pin 6

    p = []
    Switch = 0
    Servo = 0
    openPosition = 0.40
    closedPosition = -0.05
    State = ''

    def __init__(self, Switch, Servo):
        #setup pins
        self.Switch = Switch
        self.Servo = Servo
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Switch,GPIO.IN)
        GPIO.setup(Servo,GPIO.OUT)
        self.p=GPIO.PWM(Servo,50)
        self.p.start(2.5)
        time.sleep(1)

    def __del__(self):
        GPIO.cleanup()

    def setServo(self, percentageVal):
        value = (12.5-2.5)*percentageVal + 2.5
        self.p.ChangeDutyCycle(value)
        time.sleep(1)
        Log.Log('        Servo set to ' + str(percentageVal*100) + '% extended')     
	
    def checkServoSwitch(self):
        if GPIO.input(self.Switch):
            self.setServo(self.openPosition)
        else:
            self.setServo(self.closedPosition)
            
    def LandServo(self):
        self.setServo(self.openPosition)
        Log.Log('Servo landing activated')
    
#need to find reset for repeat with switch change#
#Also once testing is complete operation

#******Implementation Notes*******
#import ServoControl
#servo = ServoControl.ServoControl(17,6)
#servo.checkServoSwitch()
