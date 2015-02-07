#!/bin/python

from pygatt.pygatt import *
import bluetooth
import time
import sys

def setBuzzer(bleDevice, bleHandler, modo):
    if modo:
        command = "#BZ2000\r\n"
    else:    
        command = "#BZ0\r\n"
    bleDevice.char_write(bleHandler, bytearray(command))

    return

def main():
    bleBluetoothAddress = sys.argv[1]
    modo = int(sys.argv[2])
    reset_bluetooth_controller()
    time.sleep(0.1)
    bleDevice = BluetoothLeDevice(bleBluetoothAddress)
    bleHandler = 0x11

    setBuzzer(bleDevice, bleHandler, modo)

main()
