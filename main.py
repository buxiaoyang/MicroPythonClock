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
# 7 segment led strokes array pins
arraySegPin = []
# Dig pins array used to select which digital to display
arrayDigPin = [] 
# 0~9 nunmber truth table for 7 segment led (a~g)
arraySegNumber = [[1,1,1,1,1,1,0],[0,1,1,0,0,0,0],[1,1,0,1,1,0,1],[1,1,1,1,0,0,1],[0,1,1,0,0,1,1],[1,0,1,1,0,1,1],[1,0,1,1,1,1,1],[1,1,1,0,0,0,0],[1,1,1,1,1,1,1],[1,1,1,1,0,1,1]]

# Input buttons pins
btnSetting = Pin(15, Pin.IN, Pin.PULL_DOWN)
btnUp = Pin(14, Pin.IN, Pin.PULL_DOWN)

# Variables for count the time
timeHour = 0
timeMinute = 0
timeSecond = 0

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
    """Time pulse function which to caculate time travel

    Args:
        timer: timer variable
    """
    
    # Toggle the clock dot to display
    pinClockDot.toggle()
    
    # Caculate the time travel
    global timeSecond,timeMinute,timeHour
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
    
# Call init function
Init()

while True:
    """Main loop which to handle display and button check etc
    """

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
        arrayDigPin[number].value(0)
        # Wait for display a while
        time.sleep(0.001)
        # Close the display
        arrayDigPin[number].value(1)

    # Handle key event
    if btnSetting.value():
        pinClockDot.value(0)
    if btnUp.value():
        pinClockDot.value(1)
    
    

