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
MMA8452Q_REG_CTRL_REG1 = 0x2A # Control Register 1
MMA8452Q_ODR_800 = 0x00 # 800 Hz
MMA8452Q_MODE_NORMAL = 0x00 # Normal Mode
MMA8452Q_MODE_ACTIVE = 0x01 # Active Mode

MMA8452Q_REG_XYZ_DATA_CFG = 0x0E # Data Configuration Register
MMA8452Q_DATA_CFG_FS_2 = 0x00 # Full-Scale Range = 2g
MMA8452Q_DEFAULT_ADDRESS = 29

MMA8452Q_REG_STATUS = 0x00 # Data status Register

class MMA8451():
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
        # configure the sensor
        MODE_CONFIG = (MMA8452Q_ODR_800 | MMA8452Q_MODE_NORMAL | MMA8452Q_MODE_ACTIVE) # sampling rate
        self.i2c.writeto_mem(MMA8452Q_DEFAULT_ADDRESS, MMA8452Q_REG_CTRL_REG1, MODE_CONFIG)

        DATA_CONFIG = (MMA8452Q_DATA_CFG_FS_2) # 2g
        self.i2c.writeto_mem(MMA8452Q_DEFAULT_ADDRESS, MMA8452Q_REG_XYZ_DATA_CFG, DATA_CONFIG)

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
        self.data = self.i2c.readfrom_mem(MMA8452Q_DEFAULT_ADDRESS, MMA8452Q_REG_STATUS, 6)


s = MMA8451('data.txt', 0.01)
#time.sleep(60)
#s.stop()
