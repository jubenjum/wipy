from machine import I2C, RTC, Timer
import time
import struct
import array

class ADXL345():
    def __init__(self, file_, dt=1.0):
        self.f = open(file_, 'w')
        self.dt = dt

        self.n = 0
        self.into_buf_i = 0
        self.write_i = 0
        #self.buffer_ = array.array('hhh', [0 for i in range(8192)])
        self.buff_a = []
        self.buff_t = []


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
        self.buff_a.append(self.data)
        self.buff_t.append(time.ticks_diff(self.begin, time.ticks_us()))
        #self.write_to_file()

        #self.buffer_[self.into_buf_i] = self.data
        #self.buffer_[self.into_buf_i + 3] = time.ticks_diff(time.ticks_us(), self.begin)
        #self.into_buf_i += 3

    def write_to_file(self):
        self.f.write("{} {}\n".format(self.rtc.now(), self.vals))
        #print("{} {}\n".format(self.rtc.now(), self.vals))

    def stop(self):
        self.__alarm.callback(None)
        print("n=%d"%self.n)
        for a, t in zip(self.buff_a, self.buff_t):
            self.f.write("{} {}\n".format(t,
                 struct.unpack('<hhh', a)))
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
time.sleep(60)
s.stop()

#with open('data.txt', 'w') as f:
#    s = ADXL345(f, 1)


#s.load_to_file()
