from machine import Timer
alarm = Timer.Alarm(lambda x: print("hello"), 5, periodic=True)
alarm.callback(None)
