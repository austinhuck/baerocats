from Singleton import Singleton
from xbee import ZigBee

import Queue
import serial
import struct
import threading
import time

class Radio(object):
    __metaclass__ = Singleton

    GroundAddress = b'\x00\x13\xA2\x00\x41\x26\x92\xE8'

    def __init__(self):
        self._ser = None
        self._xbee = None
        self._sendQueue = Queue.Queue()
        self._receiveQueue = Queue.Queue()
        self._thread = threading.Thread(target=self._Worker)
        self._thread.daemon = True
        self._threadShutdown = threading.Event()

    def __del__(self):
        self._threadShutdown.set()
        self._thread.join(0.1)
        self._xbee.halt()

    def _Receive(self, data):
        # Check the type of message

        # Parse the message data

        # Add the message to the receive queue
        pass

    def _Worker(self):
        while not self._threadShutdown.isSet():
            try:
                message = self._sendQueue.get(block=True, timeout=0.1)

                self._xbee.send('tx',
                                frame_id=b'\x00',
                                dest_addr_long=Radio.GroundAddress,
                                dest_addr=b'\xFF\xFE',
                                data = message.GetData())
            except Queue.Empty:
                pass
             
    def Initialize(self, port='/dev/ttyUSB0'):
        self._ser = serial.Serial(port=port, baudrate=115200)
        self._xbee = ZigBee(self._ser, callback=self._Receive)
        self._thread.start()

    def Receive(self):
        message = None

        try:
            message = self._receiveQueue.get(block=False)
        except Queue.Empty:
            pass

        return message

    def Send(self, message):
        self._sendQueue.put(message)

    def Shutdown(self):
        self._threadShutdown.set()
        self._thread.join()
        self._xbee.halt()

class Message(object):    
    # Message Type 'Enums'
    Unknown = 0
    Data = 1
    Log = 2
    Cmd = 3
    CmdResponse = 4

    # Class variables for ID tracking
    _ID = 0
    _IDLock = threading.Lock()
    
    @classmethod
    def _GetNextID(cls):
        Message._IDLock.acquire()
        
        ID = Message._ID
        
        if Message._ID >= 65535:
            Message._ID = 0
        else:
            Message._ID += 1

        Message._IDLock.release()
            
        return ID
    
    def __init__(self):
        self.ID = Message._GetNextID()
        self.Source = 2
        self.Time = long(time.time() * 1000000)
        self.Type = Message.Unknown

    def GetData(self):
        # TODO: Implement
        return struct.pack('<HBQB', self.ID, self.Source, self.Time, self.Type)
    
class DataMessage(Message):
    def __init__(self, lat, lng, ax, ay, az, qw, qx, qy, qz, wx, wy, wz, alt, light):
        Message.__init__(self)
        self.Type = Message.Data
        self.Latitude = lat
        self.Longitude = lng
        self.AccelX = ax
        self.AccelY = ay
        self.AccelZ = az
        self.QuatW = qw
        self.QuatX = qx
        self.QuatY = qy
        self.QuatZ = qz
        self.OmegaX = wx
        self.OmegaY = wy
        self.OmegaZ = wz
        self.Altitude = alt
        self.Light = light

    def GetData(self):
        # TODO: Implement
        return Message.GetData(self) + \
            struct.pack('<14f',
                        self.Latitude,
                        self.Longitude,
                        self.AccelX,
                        self.AccelY,
                        self.AccelZ,
                        self.QuatW,
                        self.QuatX,
                        self.QuatY,
                        self.QuatZ,
                        self.OmegaX,
                        self.OmegaY,
                        self.OmegaZ,
                        self.Altitude,
                        self.Light)

class LogMessage(Message):
    def __init__(self, text):
        Message.__init__(self)
        self.Type = Message.Log
        self.Length = len(text)
        self.Text = text

    def GetData(self):
        # TODO: Implement
        return Message.GetData(self) + \
            struct.pack('<Bs',
                        self.Length,
                        self.Text)
