#!/bin/python

from pygatt.pygatt import *
import bluetooth
import time
import sys


def RGBLed(bleDevice, bleHandler, color, intensidade, apagarOutros):
    ledCode = ['R', 'G', 'B']

    if ( apagarOutros ):
        if color == 0:
            command = "#LG0\r\n"
            bleDevice.char_write(bleHandler, bytearray(command))
            command = "#LB0\r\n"
            bleDevice.char_write(bleHandler, bytearray(command))
        elif color == 1:
            command = "#LR0\r\n"
            bleDevice.char_write(bleHandler, bytearray(command))
            command = "#LB0\r\n"
            bleDevice.char_write(bleHandler, bytearray(command))
        elif color == 2:
            command = "#LR0\r\n"
            bleDevice.char_write(bleHandler, bytearray(command))
            command = "#LG0\r\n"
            bleDevice.char_write(bleHandler, bytearray(command))

    #Define a intensidade do LED
    command = "#L%c%d\r\n" % (ledCode[color], intensidade)
    bleDevice.char_write(bleHandler, bytearray(command))

    return

def main():
    bleBluetoothAddress = sys.argv[1]
    color = int(sys.argv[2])
    intensidade = int(sys.argv[3])
    apagarOutros = int(sys.argv[4])
    reset_bluetooth_controller()
    time.sleep(0.1)
    bleDevice = BluetoothLeDevice(bleBluetoothAddress)
    bleHandler = 0x11

    RGBLed(bleDevice, bleHandler, color, intensidade, apagarOutros)

main()
