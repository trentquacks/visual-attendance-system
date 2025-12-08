"""
https://www.youtube.com/watch?v=UeybhVFqoeg
"""

import serial.tools.list_ports
from time import sleep

def open():
    try:
        serial_instance = serial.Serial()
        serial_instance.baudrate = 9600
        serial_instance.port = '/dev/ttyUSB0'
        serial_instance.open()
        sleep(3)
        serial_instance.write("OPEN".encode('utf-8'))
        sleep(3)
    except Exception as e: 
        print("Arduino Error:", e)

open()
