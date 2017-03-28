import TDC
import time

tdc = TDC.TDC()

tdc.Initialize()

tdc.Record(0.5)

print "Enter Sleep"
time.sleep(5)
print "Exit Sleep"
tdc.Stop()
print "Stop Done"c