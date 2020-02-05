from machine import I2C, RTC, Timer
import time
import struct
import array

class ADXL345():
    def __init__(self, file_, dt=1.0):
        self.f = file_
        self.dt = dt

        self.rtc = RTC()
        self.i2c = I2C()
        self._setup()
        self.n = 0

        self.__alarm = Timer.Alarm(self._handler, dt, periodic=True)

    def _setup(self):
        # configure the sensor
        self.i2c.writeto_mem(83, 0x2C, 0x0A) # sampling rate
        self.i2c.writeto_mem(83, 0x2D, 0x08) # sampling rate 100 Hz
        self.i2c.writeto_mem(83, 0x31, 0x08) # data format

    def _handler(self, alarm):
        #self.n += 1
        #print("%03d" % self.n)
        self.get_data()
        self.write_to_file()

    def write_to_file(self):
        #date = self.rtc.now()
        #date_ = date[7] + float(date[6])*1e6 + float(date[5])*1e6*60 + float(date[4])*1e6*24*60
        #self.f.write("{}\n".format(self.vals))
        self.f.write("{} {}\n".format(self.rtc.now(), self.vals))
        #print("{} {}\n".format(self.rtc.now(), self.vals))

    def stop(self):
        self.__alarm.callback(None)
        self.f.close()

    def get_data(self):
        data = self.i2c.readfrom_mem(83, 0x32, 6)
        self.vals = struct.unpack('<hhh', data)

    def load_to_file(self):
        with open('data.txt', 'w') as f:
            while 1:
                self.get_data()
                f.write("{} {}\n".format(self.rtc.now(), self.vals))
                # print(rtc.now(), vals)
                time.sleep(self.dt)

f = open('data.txt', 'w')
s = ADXL345(f, 0.01)
time.sleep(600)
s.stop()

#with open('data.txt', 'w') as f:
#    s = ADXL345(f, 1)


#s.load_to_file()
