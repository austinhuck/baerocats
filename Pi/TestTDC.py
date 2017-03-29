import TDC
import time

tdc = TDC.TDC()

tdc.Initialize()

while True:
    alt = tdc.GetAltitude()
    print alt
    #print ((wx**2+wy**2+wz**2)**(.5))

    #print((wx**2+wy**2+wz**2)**(1/2))
    time.sleep(0.1)
