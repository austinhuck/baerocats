
##Change Log
##Brandon(2-1-2017): commented out GPS commands
##Austin(2-12-2017): Add fixed GPS commands


import os
import time
import threading
import gps
import Transmitting

from Singleton import Singleton
from Logger import Log
from Adafruit_BNO055 import BNO055
from tsl2561 import TSL2561
from MPL3115A2 import *

class TDC:
    __metaclass__ = Singleton
    
    # TDC Configuration
    _imuRecord = True
    _gpsRecord = True
    _lightRecord = False # Do Not Change
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
        self._imuValid = False
        self._altitude = 0.0
        self._pressure = 0.0
        self._altimeterValid = False
        self._lightLevel = 0.0
        self._lightSensorValid = False

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
                self._ReadAccel()

                #Orientation
                self._ReadQuat()

                #Rotation Rates
                self._ReadRot()

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
                self._ReadLight()

                sample+=str(self._lightLevel)
            
            if TDC._altRecord:
                sample+=","

        if TDC._altRecord:
            #Get exclusive access to the altimeter and associated data
            with self._altLock:
                #altitude in feet
                self._ReadAlt()

                #presure in psf
                self._ReadPressure()

                sample+=str(self._altitude)

        return sample + os.linesep

    def _GpsWorker(self):
        while not self._gpsStopEvent.isSet():
            try:
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
                            self._fix = False

                        # Get latitude and longitude attributes.
                        if hasattr(sample, 'lat'):
                            self._latitude = sample.lat
                        if hasattr(sample, 'lon'):
                            self._longitude = sample.lon
            except Exception as e:
                Log.Log(str(e))

    def _IsRecording(self):
        return not self._tdcStopEvent.isSet() and self._tdcThread.isAlive()

    def _RadioWorker(self):
        while not self._radioStopEvent.isSet():
            try:
                msg = Transmitting.DataMessage(\
                    self._latitude, self._longitude,\
                    self._accelX, self._accelY, self._accelZ,\
                    self._orientW, self._orientX, self._orientY, self._orientZ,\
                    self._rotrateX, self._rotrateY, self._rotrateZ,\
                    self._altitude, self._lightLevel)

                self._radio.Send(msg)
                self._radioStopEvent.wait(1)
            except Exception as e:
                Log.Log("Error transmitting data message: " + e.message)

    def _ReadAccel(self):
        try:
            #ax, ay, az - acceleration in ft/s^2
            self._accelX, self._accelY, self._accelZ = [x * 3.28084 for x in self._bno.read_accelerometer()]
            self._imuValid = True
        except Exception as e:
            Log.Log("Error reading acceleration from IMU: " + e.message)
            self._imuValid = False

    def _ReadAlt(self):
        try:
            #altitude in feet
            self._altitude = self._mpl.altitude() * 3.28084
            self._altimeterValid = True
        except Exception as e:
            Log.Log("Error reading altitude: " + e.message)
            self._altimeterValid = False

    def _ReadLight(self):
        #light in lux
        try:
            self._lightLevel = self._tsl.lux()
            self._lightSensorValid = True
        except Exception as e:
            Log.Log('Oversaturated Light Sensor')
            self._lightSensorValid = False
            self._lightLevel = 30000
            Log.Log("Error reading from light sensor: " + e.message)
            
    def _ReadPressure(self):
        try:
            #pressure in psf
            self._pressure = self._mpl.pressure() * 0.0208854
            self._altimeterValid = True
        except Exception as e:
            Log.Log("Error reading pressure: " + e.message)
            self._altimeterValid = False

    def _ReadQuat(self):
        try:
            #qw, qx, qy, qz - quaternion unitless
            self._orientW, self._orientX, self._orientY, self._orientZ = self._bno.read_quaternion()
            self._imuValid = True
        except Exception as e:
            Log.Log("Error reading orientation from IMU: " + e.message)
            self._imuValid = False

    def _ReadRot(self):
        try:
            #wx, wy, wz - rotation in radians/second
            self._rotrateX, self._rotrateY, self._rotrateZ = self._bno.read_gyroscope()
            self._imuValid = True
        except Exception as e:
            Log.Log("Error reading rotation rates from IMU: " + e.message)
            self._imuValid = False
        
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
                dataString = self._GetSampleString()
                self._dataFile.write(dataString)
                self._tdcStopEvent.wait(self._interval)
        except Exception as e:
            Log.Log(str(e))
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

        self._radio = Transmitting.Radio()
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
            if not (self._IsRecording() and TDC._imuRecord):
                self._ReadAccel()
            return self._accelX, self._accelY, self._accelZ#, self._imuValid

    def GetAltitude(self):
        with self._altLock:
            if not (self._IsRecording() and TDC._altRecord):
                self._ReadAlt()
            return self._altitude#, self._altimeterValid

    def GetGpsPosition(self):
        with self._gpsLock:
            return self._fix, self._latitude, self._longitude

    def GetLightLevel(self):
        with self._lightLock:
            self._ReadLight()
            return self._lightLevel#, self._lightSensorValid

    def GetOrientation(self):
        with self._imuLock:
            if not (self._IsRecording() and TDC._imuRecord):
                self._ReadQuat()
            return self._orientW, self._orientX, self._orientY, self._orientZ#, self._imuValid

    def GetPressure(self):
        with self._altLock:
            if not (self._IsRecording() and TDC._altRecord):
                self._ReadPressure()
            return self._pressure#, self._altimeterValid

    def GetRotationRate(self):
        with self._imuLock:
            if not (self._IsRecording() and TDC._imuRecord):
                self._ReadRot()
            return self._rotrateX, self._rotrateY, self._rotrateZ#, self._imuValid

    def GetIMUValid(self):
        return self._imuValid

    def GetLightValid(self):
        return self._lightSensorValid

    def GetAltimeterValid(self):
        return self._altimeterValid

    def GetGpsValid(self):
        return self._fix


    def Record(self, interval):
        self._interval = interval
        self._tdcStopEvent.clear()
        self._radioStopEvent.clear()
        self._tdcThread.start()
        self._radioThread.start()
        return self._tdcThread.isAlive() and self._radioThread.isAlive()

    def Stop(self):
        # Flag worker thread to stop and wait for stop
        self._radioStopEvent.set()
        self._radioThread.join()
        self._tdcStopEvent.set()
        self._tdcThread.join()
        return not self._tdcThread.isAlive() and not self._radioThread.isAlive()
