from machine import Pin, PWM
from time import sleep

pin1 = Pin(16, Pin.OUT)
pin2 = Pin(17, Pin.OUT)
pin3 = Pin(18, Pin.OUT)
pin4 = Pin(19, Pin.OUT)
pin1.value(1)
pin2.value(1)
pin3.value(1)
pin4.value(1)

pin9 = Pin(9, Pin.OUT)

pwm = PWM(Pin(8))

pwm.freq(100000)

while True:
    pin9.toggle()
    for duty in range(65536):
        pwm.duty_u16(duty)
        sleep(0.0001)
    pin9.toggle()
    for duty in range(65536, 0, -1):
        pwm.duty_u16(duty)
        sleep(0.0001)