"""MicroPython Clock
   Author: Bu, Xiao-Yang (Shawn)
   Date: March 23, 2022
"""

from machine import Pin, I2C, Timer, PWM
import machine
import time

# Timer use for generate 0.5s pulse
timer = Timer()

# The photoresistance pin used to read brightness value
brightnessADC = machine.ADC(28)

# I2C for communicate with PCF8563 RTC chip
i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=100000)

# Number dot pin
pinDP = Pin(7, Pin.OUT)
# Clock dot pin
pinClockDot = PWM(Pin(8))
pinClockDot.freq(100000)
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
timeSetState = 0
# Setting state time count, used to exist setting state after 20 second
timeSetCounter = 0
# Show clock dot or not, used to falshing the second dot
time100msCounter = 0
# LED brightness, max PWM is 65536
brightnessPWM = 65536
# LED brightness steps, the adc value is the photoresistance input while the pwm value is the brightness output
brightnessStepsADC = [62500, 62700, 62900, 63100, 63300, 63500, 63700, 63900, 64100, 64300, 64500, 64700, 64900]
brightnessStepsPWM = [65536, 60000, 55000, 50000, 45000, 40000, 35000, 30000, 25000, 20000, 15000, 10000, 5000]

def Init():
    """Init function which do init when starts
    """
    
    # Define the strokes pin number 0->a, 1->b, 2->c, 3->d, 4->e, 5->f, 6->g
    segPinList = [0,1,2,3,4,5,6]
    for seg in segPinList:
        pwm = PWM(Pin(seg))
        pwm.freq(100000)
        arraySegPin.append(pwm)
    # Define the number pin 16->dig1, 17->dig2, 18->dig3, 19->dig4
    digPinList = [16,17,18,19]
    for dig in digPinList:
        arrayDigPin.append(Pin(dig, Pin.OUT))
    # Set dp pin to value 0, which will not display at all
    pinDP.value(0)
    
    # Wait 1s for RTC to init
    time.sleep(1)
    # Init RTC, 0x51 is PCF8563's i2c address, 0x02 is it's second reg.
    i2c.writeto_mem(0x51, 0x02, b'\x00\x00\x09')
    
    # 0.5s timer, used for time count.
    timer.init(freq=2, mode=Timer.PERIODIC, callback=Pulse500ms)

def GetPWM():
    """Get PWM value
        Read the adc and use mapping steps to get PWM value
    """
    global brightnessPWM, brightnessStepsADC, brightnessStepsPWM
    
    brightnessPWM = 65536
    adcValue = brightnessADC.read_u16()
    print("ADC: ",adcValue)
    for step in range(13):
        if adcValue > brightnessStepsADC[step]:
            brightnessPWM = brightnessStepsPWM[step]

def Pulse500ms(timer):
    """Time pulse function which to caculate time travel, run every 500ms

    Args:
        timer: timer variable
    """
    global timeSetState, timeSetCounter, time100msCounter, brightness
    
    time100msCounter = time100msCounter + 1;
    # Toggle the clock dot to display
    if time100msCounter % 2 == 0:
        pinClockDot.duty_u16(brightnessPWM)
        timeClockDotShow = False
    else:
        pinClockDot.duty_u16(0)
        timeClockDotShow = True
    # Adjust the PWM every 5 seconds
    if time100msCounter % 10 == 0:
        GetPWM()
    # Flashing the set number
    if timeSetState == 1:
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
    elif timeSetState == 2:
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
        timeSetState = 0
    
def Bcd2dec(bcd):
    """Convert BCD code to Dec number
        refer to wiki for detail about BCD code: https://en.wikipedia.org/wiki/Binary-coded_decimal

    Args:
        bcd: BCD code which needs to convert to dec number
        
    Returns:
        Dec number of that bcd
        
    """
    return (((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f))
        
def Dec2bcd(dec):
    """Convert Dec number to BCD code 

    Args:
        bcd: BCD code which needs to convert to dec number
        
    Returns:
        Dec number of that bcd
        
    """
    tens, units = divmod(dec, 10)
    return (tens << 4) + units

# Call init function
Init()

while True:
    """Main loop which to handle display and button check etc
    """
    
    # Toggle the loop pulse test output (10ms for every loop)
    pinLoopPulse.toggle()
    
    # Read current time from RTC, 0x51 is PCF8563's i2c address, 0x02 is it's second reg.
    if timeSetState == 0:
        i2cMemRead = i2c.readfrom_mem(0x51, 0x02, 3)
        timeHour = Bcd2dec(i2cMemRead[2] & 0x3F)
        timeMinute = Bcd2dec(i2cMemRead[1] & 0x7F)
        #timeSecond = Bcd2dec(memRead[0] & 0x7F)
    
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
            if arraySegNumber[timeNumberArray[number]][seg] == 1:
                arraySegPin[seg].duty_u16(brightnessPWM)
            else:
                arraySegPin[seg].duty_u16(0)
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
            timeSetState = timeSetState + 1
            if timeSetState > 2:
                timeSetState = 0
                # Write setting value to RTC
                i2cMemWrite = bytearray()
                i2cMemWrite.append(Dec2bcd(0)) # Second set to 0
                i2cMemWrite.append(Dec2bcd(timeMinute)) # Minute
                i2cMemWrite.append(Dec2bcd(timeHour)) # Hour
                # 0x51 is PCF8563's i2c address, 0x02 is it's second reg.
                i2c.writeto_mem(0x51, 0x02, i2cMemWrite)
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
            if timeSetState == 1:
                # Minute set
                timeMinute = timeMinute + 1
                if timeMinute >= 60:
                    timeMinute = 0
            elif timeSetState == 2:
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
