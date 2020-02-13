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


# variables of configuration
MEASURE_MODE = 0x06 # Only accelerometer
DEVICE_ADDRESS = 0x1D
RANGE = 0x2C
RANGE_2G = 0x01
POWER_CTL = 0x2D
AXIS_START          = 0x08
AXIS_LENGTH         = 9

class ADXL355():
    def __init__(self, file_, dt=1.0):
        self.dt = dt
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while 1:
            try:
                self.s.connect((HOST, PORT))
                self.socket_ = True
            except:
                time.sleep(1)
                print('no connection to {}'.format(HOST))
                self.f = open(file_, 'w')
                self.socket_ = False
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
        # range of the accelerometric data
        self.i2c.writeto_mem(DEVICE_ADDRESS, RANGE, RANGE_2G)

        #  enable measure mode
        self.i2c.writeto_mem(DEVICE_ADDRESS, POWER_CTL, MEASURE_MODE)

    def _handler(self, alarm):
        self.n += 1
        self.get_data()

        self.buf_0[self.buf_index][0] = time.ticks_diff(self.begin, time.ticks_ms())

        axisX = (self.data[0] << 16 | self.data[1] << 8 | self.data[2]) >> 4
        axisY = (self.data[3] << 16 | self.data[4] << 8 | self.data[5]) >> 4
        axisZ = (self.data[6] << 16 | self.data[7] << 8 | self.data[8]) >> 4

        if(axisX & (1 << 20 - 1)):
            axisX = axisX - (1 << 20)

        if(axisY & (1 << 20 - 1)):
            axisY = axisY - (1 << 20)

        if(axisZ & (1 << 20 - 1)):
            axisZ = axisZ - (1 << 20)

        self.buf_0[self.buf_index][1] = [axisX, axisY, axisZ]
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
        self.data = self.i2c.readfrom_mem(DEVICE_ADDRESS, AXIS_START, AXIS_LENGTH)


s = ADXL355('data.txt', 0.01)
time.sleep(60)
s.stop()
