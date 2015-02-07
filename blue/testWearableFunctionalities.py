#!/bin/python

from pygatt.pygatt import *
import bluetooth
import sys
import time
from termcolor import colored

def getReplyId(reply):
    try:
        return reply[:3]
    except:
        return ""

def getReplyValue(reply):
    try:
        return int(reply[3:-4])
    except:
        return 0


# Test Accelerometer
def testAccelerometer(testNumber, bleDevice, bleHandler):
    failure = False
    accelerometerAxis = ['X', 'Y', 'Z']
    for i in range(3):
        print "%d-%d. Testing accelerometer reading for %c axis:" % (testNumber, i + 1, accelerometerAxis[i])
        print "\t\tNote: the device shoud be laying on a flat surface."
        command = "#AC" + str(i) + "\r\n"
        bleDevice.char_write(bleHandler, bytearray(command), wait_for_response = True)
        try:
            reply = bleDevice.char_write(bleHandler, bytearray(command), get_response = True)
            reply = str(reply)
        except:
            reply = ""
        print "\tReceived reply: ", reply[:-4]
        replyId = getReplyId(reply)
        replyValue = getReplyValue(reply)
        if len(reply) == 0:
            failure = True
            print colored("\tFailure: device does not answer.", "red")
        elif replyId != "#AC":
            failure = True
            print colored("\tFailure: incorrect reply identifier received.", "red")
        elif replyValue < -30 or replyValue > 30:
            failure = True
            print colored("\tFailure: reply value not in range [-30, +30].", "red")
        else:
            print colored("\tSuccess", "green")
    return failure

# Test Light Sensor
def testLightSensor(testNumber, bleDevice, bleHandler):
    print "%d.   Testing light sensor reading:" % testNumber
    failure = False
    command = "#LI0\r\n"
    bleDevice.char_write(bleHandler, bytearray(command), wait_for_response = True)
    try:
        reply = bleDevice.char_write(bleHandler, bytearray(command), get_response = True)
        reply = str(reply)
    except:
        reply = ""
    print "\tReceived reply: ", reply[:-4]
    replyId = getReplyId(reply)
    replyValue = getReplyValue(reply)
    if len(reply) == 0:
        failure = True
        print colored("\tFailure: device does not answer.", "red")
    elif replyId != "#LI":
        failure = True
        print colored("\tFailure: incorrect reply identifier received.", "red")
    elif replyValue < 0 or replyValue > 999:
        failure = True
        print colored("\tFailure: reply value not in range [0, 999].", "red")
    else:
        print colored("\tSuccess", "green")
    return failure

# Test Temperature Sensor
def testTemperatureSensor(testNumber, bleDevice, bleHandler):
    print "%d.   Testing temperature sensor reading:" % testNumber
    failure = False
    command = "#TE0\r\n"
    bleDevice.char_write(bleHandler, bytearray(command), wait_for_response = True)
    try:
        reply = bleDevice.char_write(bleHandler, bytearray(command), get_response = True)
        reply = str(reply)
    except:
        reply = ""
    print "\tReceived reply: ", reply[:-4]
    replyId = getReplyId(reply)
    replyValue = float(reply[3:]) if len(reply) > 0 else ""
    if len(reply) == 0:
        failure = True
        print colored("\tFailure: device does not answer.", "red")
    elif replyId != "#TE":
        failure = True
        print colored("\tFailure: incorrect reply identifier received.", "red")
    elif replyValue < 10.0 or replyValue > 40.0:
        failure = True
        print colored("\tFailure: reply value not in range [10.0, 40.0].", "red")
    else:
        print colored("\tSuccess", "green")
    return failure

# Test RGB LED
def testRgbLed(testNumber, bleDevice, bleHandler):
    ledColor = ["red", "green", "blue"]
    ledCode = ['R', 'G', 'B']
    failure = False
    for i in range(3):
        print "%d-%d. Testing RGB LED:" % (testNumber, i + 1)
        command = "#L%c0\r\n" % ledCode[i]
        bleDevice.char_write(bleHandler, bytearray(command))
        command = "#L%c255\r\n" % ledCode[i]
        bleDevice.char_write(bleHandler, bytearray(command))
        userInput = raw_input("\tIs the LGB LED bright %s? ([y]/n): " % ledColor[i])
        if userInput == "y" or userInput == "":
            print colored("\tSuccess", "green")
        else:
            print colored("\tFailure: RGB LED malfunction.", "red")
            failure = True
        command = "#L%c0\r\n" % ledCode[i]
        bleDevice.char_write(bleHandler, bytearray(command))
    return failure

# Test Buttons
def testButtons(testNumber, bleDevice, bleHandler):
    failure = False
    for i in range(2):
        print "%d-%d. Testing button %d:" % (testNumber, i + 1, i + 1)
        print "\tWaiting for button %d to be pressed within timeout." % (i + 1)
        buttonInterrupt = False
        while not buttonInterrupt:
            time.sleep(0.5)
            command = ""
            try:
                reply = bleDevice.char_write(bleHandler, bytearray(command), get_response = True)
                reply = str(reply)
                print "\tReceived reply: ", reply[:-4]
            except:
                print colored("\tFailure: button %d malfunction." % (i + 1), "red")
                failure = True
                break

            if reply[:-4] == "#B%d 1" % (i + 1):
                buttonInterrupt = True
        if buttonInterrupt:
            print colored("\tSuccess", "green")
    return failure

# Test Buzzer
def testBuzzer(testNumber, bleDevice, bleHandler):
    print "%d.   Testing buzzer:" % testNumber
    failure = False
    command = "#BZ2000\r\n"
    bleDevice.char_write(bleHandler, bytearray(command))
    time.sleep(1)
    command = "#BZ0\r\n"
    bleDevice.char_write(bleHandler, bytearray(command))
    userInput = raw_input("\tCould you hear the sound? ([y]/n): ")
    if userInput == "y" or userInput == "":
        print colored("\tSuccess", "green")
    else:
        print colored("\tFailure: buzzer malfunction.", "red")
        failure = True
    return failure

testRoutines = [
        testAccelerometer,
        testLightSensor,
        testTemperatureSensor,
        testRgbLed,
        testButtons,
        testBuzzer]

def main(argv):
    try:
        edrBluetoothAddress = argv[1]
        bleBluetoothAddress = argv[2]
    except:
        print "Error: usage:\n\t\t\ttestWearableFunctionalities.py [device edr mac address] [device ble mac address]"
        return

    reset_bluetooth_controller()
    time.sleep(0.5)
    bleDevice = BluetoothLeDevice(bleBluetoothAddress)
    bleHandler = 0x11
    
    failure = False

    for i in range(len(testRoutines)):
        try:
            result = testRoutines[i](i + 1, bleDevice, bleHandler)
            if result:
                failure = True
        except:
            print colored("Unexpected failure (probably related to a random bluetooth fault), please try again.", "red")
            return 2

    bleDevice.stop()

    return int(failure)

if __name__ == "__main__":
    ret = main(sys.argv)
    time.sleep(0.5)
    sys.exit(ret)

