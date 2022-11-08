import gpiozero
import time

class DummyLed:

    def __init__(self, pin):
        pass

    def on(self):
        pass

    def off(self):
        pass

    def toggle(self):
        pass

    def blink(self, num_times, interval):
        pass
class LED:
    
    def __init__(self, pin):
        self.pin = pin
        self.led = gpiozero.LED(self.pin)
        self.state = 0

    def on(self):
        self.state = 1
        self.led.on()

    def off(self):
        self.state = 0
        self.led.off()

    def toggle(self):
        if self.state == 0:
            self.on()
        else:
            self.off()

    def blink(self, num_times = 1, interval = 0.5):
        for i in range(num_times):
            self.toggle()
            time.sleep(interval / 2)
            self.toggle()
            time.sleep(interval / 2)


