"""MicroPython Clock
   Author: Bu, Xiao-Yang (Shawn)
   Date: March 21, 2022
"""

from machine import Pin, Timer
import time

# Timer use for generate 0.5s pulse
timer = Timer()

# Number dot pin
pinDP = Pin(7, Pin.OUT)
# Clock dot pin
pinClockDot = Pin(8, Pin.OUT)
# Test output pulse for main loop
pinLoopPulse = Pin(9, Pin.OUT)
# 7 segment led strokes array pins
arraySegPin = []
# Dig pins array used to select which digital to display
arrayDigPin = [] 
# 0~9 nunmber truth table for 7 segment led (a~g)
arraySegNumber = [[1,1,1,1,1,1,0],[0,1,1,0,0,0,0],[1,1,0,1,1,0,1],[1,1,1,1,0,0,1],[0,1,1,0,0,1,1],[1,0,1,1,0,1,1],[1,0,1,1,1,1,1],[1,1,1,0,0,0,0],[1,1,1,1,1,1,1],[1,1,1,1,0,1,1]]

# Setting button define
btnSetting = Pin(15, Pin.IN, Pin.PULL_DOWN)
# Setting button key scan state. 0: No key enter 1: Key enter wating debounce 2: Key confirm 3: Key release
btnSettingKeyStep = 0
# Up button define
btnUp = Pin(14, Pin.IN, Pin.PULL_DOWN)
# Up button key scan state. 0: No key enter 1: Key enter wating debounce 2: Key confirm 3: Key continuous confirm 4: Key release
btnUpKeyStep = 0
# Used for control number flashing, 0 not display and 1 display
arrayDigFlashing = [1,1,1,1]

# Variables for the time
timeHour = 0
timeMinute = 0
timeSecond = 0
# Time setting state. 0: Not set, 1: Set minute, 2: Set hour
timeSetNumber = 0
# Setting state time count, used to exist setting state after 20 second
timeSetCounter = 0

def Init():
    """Init function which do init when starts
    """
    
    # Define the strokes pin number 0->a, 1->b, 2->c, 3->d, 4->e, 5->f, 6->g
    segPinList = [0,1,2,3,4,5,6]
    for seg in segPinList:
        arraySegPin.append(Pin(seg, Pin.OUT))
    # Define the number pin 16->dig1, 17->dig2, 18->dig3, 19->dig4
    digPinList = [16,17,18,19]
    for dig in digPinList:
        arrayDigPin.append(Pin(dig, Pin.OUT))
    # Set dp pin to value 0, which will not display at all
    pinDP.value(0)
    
    # 0.5s timer, used for time count. 
    timer.init(freq=2.00055, mode=Timer.PERIODIC, callback=Pulse500ms)

def Pulse500ms(timer):
    """Time pulse function which to caculate time travel, run every 500ms

    Args:
        timer: timer variable
    """
    
    # Toggle the clock dot to display
    pinClockDot.toggle()
    
    # Caculate the time travel
    global timeSecond,timeMinute,timeHour,timeSetNumber,timeSetCounter
    timeSecond = timeSecond + 1
    # If second is 60 then minute plus 1
    if timeSecond >= 120: # Why 120? because the pulse is 0.5s
        timeMinute = timeMinute + 1
        timeSecond = 0
    # If minute is 60 then hour plus 1
    if timeMinute >= 60:
        timeHour = timeHour + 1
        timeMinute = 0
    # If hour is 24 then set hour to 0
    if timeHour >= 24:
        timeHour = 0
    # Flashing the set number
    if timeSetNumber == 1:
        # Count time set state time
        timeSetCounter = timeSetCounter + 1
        # Flashing minute number
        if arrayDigFlashing[3] == 1:
            arrayDigFlashing[0] = 1
            arrayDigFlashing[1] = 1
            arrayDigFlashing[2] = 0
            arrayDigFlashing[3] = 0
        else:
            arrayDigFlashing[0] = 1
            arrayDigFlashing[1] = 1
            arrayDigFlashing[2] = 1
            arrayDigFlashing[3] = 1
    elif timeSetNumber == 2:
        # Count time set state time
        timeSetCounter = timeSetCounter + 1
        # Flashing hour number
        if arrayDigFlashing[1] == 1:
            arrayDigFlashing[0] = 0
            arrayDigFlashing[1] = 0
            arrayDigFlashing[2] = 1
            arrayDigFlashing[3] = 1
        else:
            arrayDigFlashing[0] = 1
            arrayDigFlashing[1] = 1
            arrayDigFlashing[2] = 1
            arrayDigFlashing[3] = 1
    else:
        # No flashing
        arrayDigFlashing[0] = 1
        arrayDigFlashing[1] = 1
        arrayDigFlashing[2] = 1
        arrayDigFlashing[3] = 1
    # Exist setting state after 20 second no operation
    if timeSetCounter > 40:
        timeSetNumber = 0
    
# Call init function
Init()

while True:
    """Main loop which to handle display and button check etc
    """
    
    # Toggle the loop pulse test output (10ms for every loop)
    pinLoopPulse.toggle()
    
    # Get 4 display number
    timeNumberArray = []
    timeNumberArray.append(int((timeHour % 100)/10))
    timeNumberArray.append(int(timeHour % 10))
    timeNumberArray.append(int((timeMinute % 100)/10))
    timeNumberArray.append(int(timeMinute % 10))
    
    # Loop 4 display numbers
    for number in range(4):
        # Display current time number
        for seg in range(7):
            arraySegPin[seg].value(arraySegNumber[timeNumberArray[number]][seg])
        # Choose right dig to display
        for dig in range(4):
            arrayDigPin[dig].value(1)
        # Determine the number flashing or not
        if arrayDigFlashing[number] == 1:
            arrayDigPin[number].value(0)
        # Wait for display a while
        time.sleep(0.002)
        # Close the display
        arrayDigPin[number].value(1)

    # Handle setting key event state machine
    if btnSettingKeyStep == 0:
        # No key enter
        if btnSetting.value():
            #Go to next step
            btnSettingKeyStep = 1
    elif btnSettingKeyStep == 1:
        # Key enter wating debounce
        btnSettingKeyStep = 2
    elif btnSettingKeyStep == 2:
        # Key confirm
        if btnSetting.value():
            # Confirm the key event now set current setting
            timeSetNumber = timeSetNumber + 1
            if timeSetNumber > 2:
                timeSetNumber = 0
                # Reset the second to 0 every confirm setting
                timeSecond = 0
            # Rest the time setting counter
            timeSetCounter = 0
            # Go to key release
            btnSettingKeyStep = 3
        else:
            # Jitter detected, reset the state machine
            btnSettingKeyStep = 0
    elif btnSettingKeyStep == 3:
        # Key release
        if not btnSetting.value():
            btnSettingKeyStep = 0
            
    # Handle up key event state machine
    if btnUpKeyStep == 0:
        # No key enter
        if btnUp.value():
            #Go to next step
            btnUpKeyStep = 1
    elif btnUpKeyStep == 1:
        # Key enter wating debounce
        btnUpKeyStep = 2
    elif btnUpKeyStep == 2:
        # Key confirm
        if btnUp.value():
            # Confirm the key event now set current setting number + 1
            if timeSetNumber == 1:
                # Minute set
                timeMinute = timeMinute + 1
                if timeMinute >= 60:
                    timeMinute = 0
            elif timeSetNumber == 2:
                # Hour set
                timeHour = timeHour + 1
                if timeHour >= 24:
                    timeHour = 0
            # Rest the time setting counter
            timeSetCounter = 0
            # Go to next step
            btnUpKeyStep = 3
            # Here use time second as the 10ms counter, so need to reset it
            timeSecond = 0
        else:
            # Jitter detected, go to key realease
            btnUpKeyStep = 4
    elif btnUpKeyStep == 3:
        # Key continuous confirm
        if not btnUp.value():
            # Got to key release
            btnUpKeyStep = 4
        else:
            # continuous confirm
            timeSecond = timeSecond + 1
            if timeSecond > 10:
                # Every 100ms confirm the key (number + 1)
                btnUpKeyStep = 2
    elif btnUpKeyStep == 4:
        # Key release
        if not btnUp.value():
            btnUpKeyStep = 0
