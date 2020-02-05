import pyb
import micropython
micropython.alloc_emergency_exception_buf(200)

# Turn on LED to indicate logging
pyb.LED(2).on()

class T_4(object):
    def __init__(self):
        # Initialise timer 4 and ADC
        self.status = 'Sample'
        self.tim = pyb.Timer(4)
        self.tim.init(freq=10000)
        self.set_start()
        self.adc = pyb.ADC('X1')
        self.buf_index = 0
        self.buf_0 = [[0, 0] for i in range(1000)]
        self.tim.callback(self.t_4_callback)

    def set_start(self):
        # Remember time of start
        self.t_start = pyb.micros()

    def store_data(self):
        # Open log file on SD-card
        f = open('/sd/log_1.txt', 'w')

        # Store buffer data to log file
        for i in range(len(self.buf_0)):
            t = self.buf_0[i][0]
            d = self.buf_0[i][1]
            value_string = '%i, %i;' %(t, d)
            f.write(value_string)

        # Close file and blink LED
        f.close()
        pyb.LED(2).off()
        pyb.LED(3).on()
        pyb.delay(500)
        pyb.LED(3).off()

    def t_4_callback(self, tim):
        # Read ADC value and current time
        value = self.adc.read()
        t = pyb.micros() - self.t_start

        # Add value and time to buffer
        self.buf_0[self.buf_index][0] = t
        self.buf_0[self.buf_index][1] = value

        # Increment buffer index until buffer is filled,
        # then disable interrupt and change status
        self.buf_index += 1
        if (self.buf_index >= len(self.buf_0)):
            self.tim.callback(None)
            self.status = 'Store'

t = T_4()
pyb.delay(1000)

# Check if logging is finished, store data if so
# Was unable to call store data or call method storing data from callback
go_on = True
while (go_on):
    if(t.status == 'Store'):
        t.store_data()
        t.status = 'Done'
        go_on = False
    else:
        pyb.delay(100)
