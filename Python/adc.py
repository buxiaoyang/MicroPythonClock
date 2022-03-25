from machine import Pin
import machine
import utime
 
analog_value = machine.ADC(28)
 
pin1 = Pin(16, Pin.OUT)
pin2 = Pin(17, Pin.OUT)
pin3 = Pin(18, Pin.OUT)
pin4 = Pin(19, Pin.OUT)
 
pin1.value(1)
pin2.value(1)
pin3.value(1)
pin4.value(1)
 
while True:
    reading = analog_value.read_u16()     
    print("ADC: ",reading)
    utime.sleep(0.2)