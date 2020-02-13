from machine import I2C, RTC, Timer
import time
import pycom
import struct
import array

try:
    import usocket as socket
except:
    import socket

pycom.heartbeat(False)

HOST = '192.168.4.2'
PORT = 80


class ADXL345():
    def __init__(self, file_, dt=1.0):
        self.dt = dt
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while 1:
            try:
                self.s.connect((HOST, PORT))
                self.socket_ = True
            except:
                time.sleep(1)
                continue
                #print('no connection to {}'.format(HOST))
                #self.f = open(file_, 'w')
                #self.socket_ = False
            break

        self.n = 0
        self.buf_index = 0
        self.buf_0_len = 1
        self.buf_0 = [[0, 0, 0] for i in range(self.buf_0_len)]

        self.rtc = RTC()
        self.i2c = I2C(baudrate=400000)
        self._setup()
        self.begin = time.ticks_ms()

        self.__alarm = Timer.Alarm(self._handler, dt, periodic=True)

    def _setup(self):
        # configure the sensor
        self.i2c.writeto_mem(83, 0x2C, 0x0A) # sampling rate
        self.i2c.writeto_mem(83, 0x2D, 0x08) # sampling rate 100 Hz
        self.i2c.writeto_mem(83, 0x31, 0x08) # data format

    def _handler(self, alarm):
        self.n += 1
        self.get_data()

        self.buf_0[self.buf_index][0] = time.ticks_diff(self.begin, time.ticks_ms())
        self.buf_0[self.buf_index][1] = struct.unpack('<hhh', self.data)
        self.buf_0[self.buf_index][2] = struct.pack('l', time.ticks_diff(self.begin, time.ticks_ms()))

        self.buf_index += 1
        if self.buf_index >= self.buf_0_len:
            self.write_to_file()
            self.buf_index = 0

    def format_buf(self, i):
        return b"{} {} {} {}\n".format(self.buf_0[i][0],\
            self.buf_0[i][1][0], self.buf_0[i][1][1], self.buf_0[i][1][2])

    def write_to_file(self):
        for i in range(len(self.buf_0)):
            if self.socket_:
                self.s.sendall(self.format_buf(i))
            else: # save to a file
                self.f.write(self.format_buf(i))

    def stop(self):
        self.__alarm.callback(None)
        print("n=%d"%self.n)
        for i in range(self.buf_index):
            if self.socket_:
                self.s.sendall(self.format_buf(i))
            else: # save to a file
                self.f.write(self.format_buf(i))

        if self.socket_:
            self.s.close()
        else:
            self.f.close()

    def get_data(self):
        self.data = self.i2c.readfrom_mem(83, 0x32, 6)


s = ADXL345('data.txt', 0.01)
#time.sleep(60)
#s.stop()
