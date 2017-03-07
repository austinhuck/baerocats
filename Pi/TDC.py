
##Change Log
##Brandon(2-1-2017): commented out GPS commands
##Austin(2-12-2017): Add fixed GPS commands


import os
import time
import threading
import struct
import gps
import serial
import Transmitting

from Singleton import Singleton
from Logger import Log
from spidev import SpiDev
from Adafruit_BNO055 import BNO055
from tsl2561 import TSL2561
from MPL3115A2 import *

class TDC:
    __metaclass__ = Singleton
    
    # TDC Configuration
    _imuRecord = True
    _gpsRecord = True
    _lightRecord = True
    _altRecord = True
    
    def __init__(self):
        # Data Variables
        self._fix = False
        self._latitude = 0.0
        self._longitude = 0.0
        self._accelX = 0.0
        self._accelY = 0.0
        self._accelZ = 0.0
        self._orientW = 0.0
        self._orientX = 0.0
        self._orientY = 0.0
        self._orientZ = 0.0
        self._rotrateX = 0.0
        self._rotrateY = 0.0
        self._rotrateZ = 0.0
        self._altitude = 0.0
        self._pressure = 0.0
        self._lightLevel = 0.0

        # Sync Objects
        self._gpsLock = threading.Lock()
        self._imuLock = threading.Lock()
        self._altLock = threading.Lock()
        self._lightLock = threading.Lock()

        # Communication/Control Variables
        self._interval = 0
        self._tdcStopEvent = None
        self._tdcThread = None
        self._gpsStopEvent = None
        self._gpsThread = None
        self._radio = None
        self._radioThread = None
        self._radioStopEvent = None

        # Sensor Variables
        self._tsl = None
        self._mpl = None
        self._bno = None
        self._gps = None

        #Flight Data location
        self._dataFileDir = Log.launchPath
        self._dataFilePath = os.path.join(self._dataFileDir,'FlightData.txt')
        self._dataFile = None

    def _GetHeaderString(self):
        # Build data file header
        header = 'time,'
        if TDC._imuRecord:
            header+='AX,AY,AZ,QW,QX,QY,QZ,wX,wY,wZ'
            if TDC._gpsRecord or TDC._lightRecord or TDC._altRecord:
                header+=","

        if TDC._gpsRecord:
            header+='Lat,Long'
            if TDC._lightRecord or TDC._altRecord:
                header+=","

        if TDC._lightRecord:
            header+='Lux'
            if TDC._altRecord:
                header+=","

        if TDC._altRecord:
            header+='Alt'

        return header + os.linesep

    def _GetSampleString(self):
        # Sample data and build save file string
        sample = str(time.time()-Log.t0) +','
        
        if TDC._imuRecord:
            #Get exclusive access to the IMU and associated data
            with self._imuLock:
                #Acceleration            
                self._accelX, self._accelY, self._accelZ = self._ReadAccel()

                #Orientation
                self._orientW, self._orientX, self._orientY, self._orientZ = self._ReadQuat()

                #Rotation Rates
                self._rotrateX, self._rotrateY, self._rotrateZ = self._ReadRot()
                
                sample+=  str(self._accelX) + ',' + str(self._accelY) + ',' + str(self._accelZ) + ',' + \
                              str(self._orientW) + ',' + str(self._orientX) + ',' + str(self._orientY) + ',' + str(self._orientZ) + ',' + \
                              str(self._rotrateX) + ',' + str(self._rotrateY) + ',' + str(self._rotrateZ)
            
            if TDC._gpsRecord or TDC._lightRecord or TDC._altRecord:
                sample+=","

        if TDC._gpsRecord:
            #Get exclusive access to the GPS and associated data
            with self._gpsLock:
                #_gpsThread is polling for data, take what has been saved off.
                sample+=str(self._latitude) + ',' + str(self._longitude)

            if TDC._lightRecord or TDC._altRecord:
                sample+=","

        if TDC._lightRecord:
            #Get exclusive access to the light sensor and associated data
            with self._lightLock:            
                #light level
                self._lightLevel = self._ReadLight()
                sample+=str(self._lightLevel)
            
            if TDC._altRecord:
                sample+=","

        if TDC._altRecord:
            #Get exclusive access to the altimeter and associated data
            with self._altLock:
                #altitude in feet
                self._altitude = self._ReadAlt()
                #presure in psf
                self._pressure = self._ReadPressure()
            
                sample+=str(self._altitude)

        return sample + os.linesep

    def _GpsWorker(self):
        while not self._gpsStopEvent.isSet():
            sample = self._gps.next()
            if sample['class'] == 'TPV':
                with self._gpsLock:
                    # TODO: Sync pi system time
                    if hasattr(sample, 'time'):
                        pass

                    # Determine the fix, this may not always be present.
                    if hasattr(sample, 'fix'):
                        self._fix = sample.fix
                    else:
                        self._fix = false

                    # Get latitude and longitude attributes.
                    if hasattr(sample, 'lat'):
                        self._latitude = sample.lat
                    if hasattr(sample, 'lon'):
                        self._longitude = sample.lon

    def _IsRecording(self):
        return not self._tdcStopEvent.isSet() and self._tdcThread.isAlive()

    def _RadioWorker(self):
        while not self._radioStopEvent.isSet():
##            with self._imuLock:
##                with self._gpsLock:
##                    with self._altLock:
##                        with self._lightLock:
            msg = Transmitting.DataMessage(\
                self._latitude, self._longitude,\
                self._accelX, self._accelY, self._accelZ,\
                self._orientW, self._orientX, self._orientY, self._orientZ,\
                self._rotrateX, self._rotrateY, self._rotrateZ,\
                self._altitude, self._lightLevel)
            
            self._radio.Send(msg)
            self._radioStopEvent.wait(1)

    def _ReadAccel(self):
        #ax, ay, az - acceleration in ft/s^2
        return [x * 3.28084 for x in self._bno.read_accelerometer()]

    def _ReadAlt(self):
        #altitude in feet
        return self._mpl.altitude() * 3.28084

    def _ReadGps(self):
        #fix, latitude, longitude - Boolean and Decimal Degrees
        fix, lat, lon, heading, speed, altitude, num_sat, timestamp, datestamp = \
             self._gps.read_sensor()
        return fix, lat, lon

    def _ReadLight(self):
        #light in lux
        try:
            return self._tsl.lux()
        except:
            Log.Log('Oversaturated Light Sensor')
            return 30000
            
    def _ReadPressure(self):
         #pressure in psf
        return self._mpl.pressure() * 0.0208854

    def _ReadQuat(self):
        #qw, qx, qy, qz - quaternion unitless
        return self._bno.read_quaternion()

    def _ReadRot(self):
        #wx, wy, wz - rotation in radians/second
        return [x * 3.14159 / 180 for x in self._bno.read_gyroscope()]
        
    def _TdcWorker(self):
        try:
            #Open up the output file and print the header
            self._dataFile = open(self._dataFilePath, 'w+')
            self._dataFile.write(self._GetHeaderString())
                        
            Log.Log('Writing to file' + os.path.abspath(self._dataFilePath))

            if TDC._gpsRecord:
                #Start up _gpsThread
                self._gpsStopEvent.clear()
                self._gpsThread.start()

            #Continue collecting data as long as we're not signaled to stop
            while not self._tdcStopEvent.isSet():
                self._dataFile.write(self._GetSampleString())
                self._tdcStopEvent.wait(self._interval)

        finally:
            #Always close the output file
            if self._dataFile is not None:
                self._dataFile.close()
                self._dataFile = None

            if TDC._gpsRecord:
                #Always shut down _gpsThread
                self._gpsStopEvent.set()
                self._gpsThread.join()

    def Initialize(self):
        # Create output directory
        if not os.path.exists(self._dataFileDir):
            os.makedirs(self._dataFileDir)

        # Test file opening.
        try:
            self._dataFile = open(self._dataFilePath, 'w+')
            self._dataFile.close()
        finally:
            if self._dataFile is not None:
                self._dataFile.close()
                self._dataFile = None

        #self._radio = Transmitting.Radio()
        self._radioStopEvent = threading.Event()
        self._radioThread = threading.Thread(target=self._RadioWorker, name='Radio')
        self._radioThread.daemon = False

        # TODO: Add error handling for sensor init...        
        self._gps = gps.gps("localhost", "2947")
        self._gps.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self._gpsStopEvent = threading.Event()
        self._gpsThread = threading.Thread(target=self._GpsWorker, name='GPS')
        self._gpsThread.daemon = False

        self._tsl=TSL2561()

        self._mpl = MPL3115A2()

        self._bno = BNO055.BNO055()
        self._bno.begin()
        self._tdcStopEvent = threading.Event()
        self._tdcThread = threading.Thread(target=self._TdcWorker, name='TDC')
        self._tdcThread.daemon = False

    def GetAcceleration(self):
        with self._imuLock:
            # If recording then take the last saved off values
            # otherwise read values from the sensor
            if self._IsRecording() and TDC._imuRecord:
                ax = self._accelX
                ay = self._accelY
                az = self._accelZ
            else:
                ax, ay, az = self._ReadAccel()
        
        return ax, ay, az
        
    def GetAltitude(self):
        with self._altLock:        
            if self._IsRecording() and TDC._altRecord:
                alt = self._altitude
            else:
                alt = self._ReadAlt()
                
        return alt

    def GetGpsPosition(self):
        with self._gpsLock:        
            if self._IsRecording() and TDC._gpsRecord:
                fix = self._fix
                lat = self._latitude
                lng = self._longitude
            else:
                fix, lat, lng = self._ReadGps()

        return fix, lat, lng

    def GetLightLevel(self):
        with self._lightLock:
            if self._IsRecording() and TDC._lightRecord:
                light = self._lightLevel
            else:
                light = self._ReadLight()
            
        return light

    def GetOrientation(self):
        with self._imuLock:
            if self._IsRecording() and TDC._imuRecord:
                qw = self._orientW
                qx = self._orientX
                qy = self._orientY
                qz = self._orientZ
            else:
                qw, qx, qy, qz = self._ReadQuat()

        return qw, qx, qy, qz

    def GetPressure(self):
        with self._altLock:
            if self._IsRecording() and TDC._altRecord:
                pressure = self._pressure
            else:
                pressure = self._ReadPressure()

        return pressure

    def GetRotationRate(self):
        with self._imuLock:
            if self._IsRecording() and TDC._imuRecord:
                rx = self._rotrateX
                ry = self._rotrateY
                rz = self._rotrateZ
            else:
                rx, ry, rz = self._ReadRot()

        return rx, ry, rz

    def Record(self, interval):
        self._interval = interval
        self._tdcStopEvent.clear()
        self._radioStopEvent.clear()
        self._tdcThread.start()
        #self._radioThread.start()
        return self._tdcThread.isAlive() and self._radioThread.isAlive()

    def Stop(self, timeout=5):
        # Flag worker thread to stop and wait for stop
        self._radioStopEvent.set()
        self._tdcStopEvent.set()
        #self._radioThread.join(timeout)
        self._tdcThread.join(timeout)
        return not self._tdcThread.isAlive() and not self._radioThread.isAlive()
