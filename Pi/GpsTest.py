import gps
import threading
import time

_fix = False
_latitude = 0.0
_longitude = 0.0
_gpsStopEvent = None
_gpsThread = None

def _GpsWorker():
    global _fix, _latitude, _longitude, _gpsStopEvent
    while not _gpsStopEvent.isSet():
        print "Waiting"
        sample = _gps.next()
        print "Recieved {0}".format(sample['class'])
        if sample['class'] == 'TPV':
            
            if hasattr(sample, 'time'):
                print "time"
                pass
            if hasattr(sample, 'fix'):
                print "fix"
                _fix = sample.fix
            else:
                _fix = False

            if hasattr(sample, 'lat'):
                print "lat"
                _latitude = sample.lat

            if hasattr(sample, 'lon'):
                print "lon"
                _longitude = sample.lon

_gps = gps.gps("localhost", "2947")
_gps.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
_gpsStopEvent = threading.Event()
_gpsThread = threading.Thread(target=_GpsWorker, name='GPS')
_gpsThread.daemon = False
_gpsStopEvent.clear()
_gpsThread.start()

try:
    while True:
        print "{0}, {1}, {2}".format(_fix, _latitude, _longitude)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
_gpsStopEvent.set()
