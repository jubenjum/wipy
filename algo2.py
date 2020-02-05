import pyb
import time
import micropython
micropython.alloc_emergency_exception_buf(200)
import os
import array

class logger():
    def __init__(self, timer_, freq_, file_name):
        self.block = 1024 # * sizeof(int) = 4096
        # size of buffer should be n * self.block. and a factor of data points
        self.buffer_ = array.array('i', [0 for i in range(8192)])

        self.write_data_ = self.write_data

        self.into_buf_i = 0
        self.write_i = 0
        self.max_i = len(self.buffer_)
        self.looped = False
        self.writing = False
        self.error = False

        self.timer = pyb.Timer(timer_, freq = freq_)
        self.sensor = pyb.ADC('X1')
        self.file_ = open(file_name, 'wb')

        self.begin = time.ticks_us()
        self.timer.callback(self.buffer_data)

    def terminate(self):
        if not self.error:
            self.timer.callback(None)
            time.sleep_ms(500)
            while self.writing:
                pass
            if self.looped:
                self.file_.write(self.buffer_[self.write_i:self.max_i])
                self.write_i = 0
            if self.into_buf_i != 0:
                self.file_.write(self.buffer_[self.write_i:self.into_buf_i])

            self.file_.close()

    def buffer_data(self, timer_):
        self.buffer_[self.into_buf_i] = self.sensor.read()
        self.buffer_[self.into_buf_i + 1]\
            = time.ticks_diff(time.ticks_us(), self.begin)
        self.into_buf_i += 2

        if self.write_i + self.block < self.into_buf_i or self.looped:
            if not self.writing:
                self.writing = True
                micropython.schedule(self.write_data_, 0)

        if self.into_buf_i >= self.max_i:
            self.into_buf_i = 0
            self.looped = True

        if self.looped and self.into_buf_i >= self.write_i:
            self.timer.callback(None)
            self.error = True
            self.file_.close()

    def write_data(self, _):
        while self.write_i + self.block < self.into_buf_i or\
              (self.looped and self.write_i < self.max_i):
            tmp = self.write_i + self.block
            self.file_.write(self.buffer_[self.write_i:tmp])
            self.write_i = tmp
            if self.write_i >= self.max_i:
                self.write_i = 0
                self.looped = False

        self.writing = False


yellow = pyb.LED(3)
blue = pyb.LED(4)
os.chdir('/sd')

blue.off()
yellow.on()
data_set = logger(4, 7000, 'data-set.bin')
time.sleep(1)
yellow.off()
if data_set.error:
    blue.on()
data_set.terminate()
