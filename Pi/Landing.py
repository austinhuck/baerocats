import TDC
import numpy as np

def Landing(WThresh,DescRateThresh,BlockSize,SampleRate):
    #Averages descent rate and IMU angular velocities over a block of BlockSize 
    # samples and waits for them to fall within the specified thresholds that qualify landing

    #initialize variables...
    Landing=0
    W=np.zeros(BlockSize)
    DescRate=np.zeros(BlockSize)
    PauseTime=1/SampleRate

    #initial sample...
    wx,wy,wz=TDC.GetRotationRate()
    w0=(wx**2+wy**2+wz**2)**0.5 #angular velocity of TRIPOD
    t0=time.time()
    Alt0=TDC.GetAltitude()

    for count in range(0,BlockSize):
        if count<BlockSize-1: #if block is not filled, keep taking data for current block
            time.sleep(PauseTime) #sleep for dt
            #Sample data...
            wx,wy,wz=TDC.GetRotationRate()
            w1=(wx**2+wy**2+wz**2)**0.5 #angular velocity of TRIPOD
            t1=time.time()
            Alt1=TDC.GetAltitude()
            dt=(t0-t1)
            DescRate[count]=(Alt1-Alt0)/dt #descent rate of TRIPOD over dt
            W[count]=(w0+w1)/2 #average angular velocity over dt
            w0=w1
            t0=t1
            Alt0=Alt1
        else: #block is filled: average data over block
            wAvg=sum(w)/len(w)
            DescRateAvg=sum(w)/len(w)
            if wAvg<WThresh and abs(DescRateAvg)<DescRateThresh:
                Landing=1
            block=block+1
    return Landing