import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

class LED:

    def __init__(self, pin: int):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, True)

    def off(self):
        GPIO.output(self.pin, False)

    def blink(self):
        time.sleep(0.1)
        self.on()
        time.sleep(0.1)
        self.off()

class Blue(LED):

    def __init__(self):
        super().__init__(26)

class Red(LED):

    def __init__(self):
        super().__init__(13)

class Green(LED):

    def __init__(self):
        super().__init__(19)

