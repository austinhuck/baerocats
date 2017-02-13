import Adafruit_GPIO.I2C as I2C
#from sys import exit

#I2C ADDRESS/BITS

MPL3115A2_ADDRESS = (0x60)

#REGISTERS

MPL3115A2_REGISTER_STATUS = (0x00)
MPL3115A2_REGISTER_STATUS_TDR = 0x02
MPL3115A2_REGISTER_STATUS_PDR = 0x04
MPL3115A2_REGISTER_STATUS_PTDR = 0x08

MPL3115A2_REGISTER_PRESSURE_MSB = (0x01)
MPL3115A2_REGISTER_PRESSURE_CSB = (0x02)
MPL3115A2_REGISTER_PRESSURE_LSB = (0x03)

MPL3115A2_REGISTER_TEMP_MSB = (0x04)
MPL3115A2_REGISTER_TEMP_LSB = (0x05)

MPL3115A2_REGISTER_DR_STATUS = (0x06)

MPL3115A2_OUT_P_DELTA_MSB = (0x07)
MPL3115A2_OUT_P_DELTA_CSB = (0x08)
MPL3115A2_OUT_P_DELTA_LSB = (0x09)

MPL3115A2_OUT_T_DELTA_MSB = (0x0A)
MPL3115A2_OUT_T_DELTA_LSB = (0x0B)

MPL3115A2_BAR_IN_MSB = (0x14)

MPL3115A2_WHOAMI = (0x0C)

#BITS

MPL3115A2_PT_DATA_CFG = 0x13
MPL3115A2_PT_DATA_CFG_TDEFE = 0x01
MPL3115A2_PT_DATA_CFG_PDEFE = 0x02
MPL3115A2_PT_DATA_CFG_DREM = 0x04

MPL3115A2_CTRL_REG1 = (0x26)
MPL3115A2_CTRL_REG1_SBYB = 0x01
MPL3115A2_CTRL_REG1_OST = 0x02
MPL3115A2_CTRL_REG1_RST = 0x04
MPL3115A2_CTRL_REG1_OS1 = 0x00
MPL3115A2_CTRL_REG1_OS2 = 0x08
MPL3115A2_CTRL_REG1_OS4 = 0x10
MPL3115A2_CTRL_REG1_OS8 = 0x18
MPL3115A2_CTRL_REG1_OS16 = 0x20
MPL3115A2_CTRL_REG1_OS32 = 0x28
MPL3115A2_CTRL_REG1_OS64 = 0x30
MPL3115A2_CTRL_REG1_OS128 = 0x38
MPL3115A2_CTRL_REG1_RAW = 0x40
MPL3115A2_CTRL_REG1_ALT = 0x80
MPL3115A2_CTRL_REG1_BAR = 0x00
MPL3115A2_CTRL_REG2 = (0x27)
MPL3115A2_CTRL_REG3 = (0x28)
MPL3115A2_CTRL_REG4 = (0x29)
MPL3115A2_CTRL_REG5 = (0x2A)

MPL3115A2_REGISTER_STARTCONVERSION = (0x12)

class MPL3115A2(object):
    '''Driver for the MPL3115A2 altitude sensor.'''
    def __init__(self, address=None, busnum=None, debug=False):
        if address is not None:
            self.address = address
        else:
            self.address = MPL3115A2_ADDRESS

        self.i2c = I2C.get_i2c_device(self.address, busnum=busnum)

        self.debug = debug

        self._begin()

    def _begin(self):
        whoami = self.i2c.readU8(MPL3115A2_WHOAMI)
        if whoami != 0xc4:
            raise Exception("MPL3115A2 not found!")

        self.i2c.write8(
            MPL3115A2_CTRL_REG1,
            MPL3115A2_CTRL_REG1_SBYB |
            MPL3115A2_CTRL_REG1_OS128 |
            MPL3115A2_CTRL_REG1_ALT)

        self.i2c.write8(
            MPL3115A2_PT_DATA_CFG, 
            MPL3115A2_PT_DATA_CFG_TDEFE |
            MPL3115A2_PT_DATA_CFG_PDEFE |
            MPL3115A2_PT_DATA_CFG_DREM)

    def poll(self):
        sta = 0
        while not (sta & MPL3115A2_REGISTER_STATUS_PDR):
            sta = self.i2c.readU8(MPL3115A2_REGISTER_STATUS)


    def altitude(self):
        self.i2c.write8(
            MPL3115A2_CTRL_REG1, 
            MPL3115A2_CTRL_REG1_SBYB |
            MPL3115A2_CTRL_REG1_OS128 |
            MPL3115A2_CTRL_REG1_ALT)

        self.poll()
        
        msb, csb, lsb = self.i2c.readList(MPL3115A2_REGISTER_PRESSURE_MSB,3)

        alt = ((msb<<24) | (csb<<16) | (lsb<<8)) / 65536.

        # correct sign
        if alt > (1<<15):
            alt -= 1<<16

        return alt


    def pressure(self):
        self.i2c.write8(
            MPL3115A2_CTRL_REG1, 
            MPL3115A2_CTRL_REG1_SBYB |
            MPL3115A2_CTRL_REG1_OS128 |
            MPL3115A2_CTRL_REG1_BAR)

        self.poll()
        
        msb, csb, lsb = self.i2c.readList(MPL3115A2_REGISTER_PRESSURE_MSB,3)

        return ((msb<<16) | (csb<<8) | lsb) / 64.

    def calibrate(self):
        pa = int(pressure()/2)
        self.i2c.writeList(MPL3115A2_BAR_IN_MSB, [pa>>8 & 0xff, pa & 0xff])

