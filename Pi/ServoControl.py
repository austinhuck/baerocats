# pylint: disable=C0103, C0111, C1001, C0326

#need to find reset for repeat with switch change#
#Also once testing is complete operation

#******Implementation Notes*******
#import ServoControl
#servo = ServoControl.ServoControl(17,6)
#servo.checkServoSwitch()

import RPi.GPIO as GPIO
import time
from Logger import Log

class ServoControl:
    #Switch is on pin 17
    #Servo is on pin 6

    Switch = 0
    Servo = 0
    State = ''

    def __init__(self, Switch, Servo):
        #setup pins
        self.Switch = Switch
        self.Servo = Servo
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Switch,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(Servo,GPIO.OUT)
        time.sleep(1)

    def __del__(self):
        GPIO.cleanup()

    def checkServoSwitch(self):
        if GPIO.input(self.Switch):
            GPIO.output(self.Servo,GPIO.HIGH)
            Log.Log('Servo Open')
        else:
            GPIO.output(self.Servo,GPIO.LOW)
            Log.Log('Servo Closed')
        time.sleep(1)
            
    def LandServo(self):
        GPIO.output(self.Servo,GPIO.HIGH)
        Log.Log('Servo landing activated')
    

