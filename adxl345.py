from machine import I2C, RTC, Timer
import time
import struct
import array

class ADXL345():
    def __init__(self, file_, dt=1.0):
        self.f = open(file_, 'w')
        self.dt = dt

        self.n = 0
        self.buf_index = 0
        self.buf_0 = [[0, 0] for i in range(1000)]

        self.rtc = RTC()
        self.i2c = I2C()
        self._setup()
        self.begin = time.ticks_us()

        self.__alarm = Timer.Alarm(self._handler, dt, periodic=True)

    def _setup(self):
        # configure the sensor
        self.i2c.writeto_mem(83, 0x2C, 0x0A) # sampling rate
        self.i2c.writeto_mem(83, 0x2D, 0x08) # sampling rate 100 Hz
        self.i2c.writeto_mem(83, 0x31, 0x08) # data format

    def _handler(self, alarm):
        self.n += 1
        self.get_data()

        self.buf_0[self.buf_index][0] = time.ticks_diff(self.begin, time.ticks_us())
        self.buf_0[self.buf_index][1] = self.data

        self.buf_index += 1
        if (self.buf_index >= len(self.buf_0)):
            self.write_to_file()
            self.buf_index = 0

    def write_to_file(self):
        for i in range(len(self.buf_0)):
            self.f.write("{} {}\n".format(self.buf_0[i][0],
                struct.unpack('<hhh', self.buf_0[i][1])))

    def stop(self):
        self.__alarm.callback(None)
        print("n=%d"%self.n)
        for i in range(self.buf_index):
            self.f.write("{} {}\n".format(self.buf_0[i][0],
                struct.unpack('<hhh', self.buf_0[i][1])))

        self.f.close()

    def get_data(self):
        self.data = self.i2c.readfrom_mem(83, 0x32, 6)
        #self.vals = struct.unpack('<hhh', self.data)

    def load_to_file(self):
        with open('data.txt', 'w') as f:
            while 1:
                self.get_data()
                f.write("{} {}\n".format(self.rtc.now(), self.vals))
                # print(rtc.now(), vals)
                time.sleep(self.dt)

s = ADXL345('data.txt', 0.005)
time.sleep(600)
s.stop()

#with open('data.txt', 'w') as f:
#    s = ADXL345(f, 1)


#s.load_to_file()
