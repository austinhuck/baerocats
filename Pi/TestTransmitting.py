import Transmitting
from Logger import Log

radio = Transmitting.Radio()

try:
    radio.Initialize()
except Exception as e:
    Log.Log(str(e))

radio.Send(Transmitting.Message())

radio.Shutdown()
