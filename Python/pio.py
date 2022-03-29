from machine import Pin
from rp2 import PIO, StateMachine, asm_pio

@asm_pio(set_init=PIO.OUT_LOW)
def square():
    wrap_target()
    set(pins, 1)
    set(pins, 0)
    wrap()
    
sm = rp2.StateMachine(0, square, freq=125000000, set_base=Pin(9))

sm.active(1)