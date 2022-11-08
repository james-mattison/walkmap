#!/usr/bin/env python3

from RPLCD import i2c
from time import sleep
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("text", action = "store")

mode = 'i2c'
cols = 20
rows = 2
charmap = 'A00'
i2c_expander = 'PCF8574'
address = 0x27
port = 1

lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap,
                  cols=cols, rows=rows)

def saything(*thing: str):
    if isinstance(thing, tuple) and len(thing) >= 2:
        line1 = thing[0]
        line2 = thing[1]
        need_clear = True
    else:
        line1 = thing[:16]
        line2 = thing[16:32]
        need_clear = len(thing) > 16

    lcd.clear()
    lcd.write_string(line1)
    if need_clear:
        lcd.crlf()
        lcd.write_string(line2)
    



if __name__ == "__main__":
    args = parser.parse_args()
    saything(args.text)
