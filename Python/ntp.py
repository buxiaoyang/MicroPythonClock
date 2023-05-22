import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import time

ssid = 'buxiaoyangiot'
password = 'buxiaoyang@123'

try:


def getNtpTime:
    
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('wifi connection failed %d' % wlan.status())
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )

    # Open a socket
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = ("203.107.6.88", 123)
    connection.connect(addr)

    # Initialize values needed to form NTP request
    packetBuffer = bytearray(48)
    # (see URL above for details on the packets)
    packetBuffer[0] = 0b11100011   # LI, Version, Mode
    packetBuffer[1] = 0     # Stratum, or type of clock
    packetBuffer[2] = 6;    # Polling Interval
    packetBuffer[3] = 0xEC  # Peer Clock Precision
    # 8 bytes of zero for Root Delay & Root Dispersion
    packetBuffer[12] = 49
    packetBuffer[13] = 0x4E
    packetBuffer[14] = 49
    packetBuffer[15] = 52

    write_len = connection.write(packetBuffer)
    print('written %d bytes to server' % write_len)

    packetBuffer = connection.read(48)
    print('read %d bytes from server' % len(packetBuffer))
    print(packetBuffer)
    timeBuffer = bytearray(4)
    timeBuffer[0] = packetBuffer[40]
    timeBuffer[1] = packetBuffer[41]
    timeBuffer[2] = packetBuffer[42]
    timeBuffer[3] = packetBuffer[43]
    print(timeBuffer)
    # convert four bytes starting at location 40 to a long integer
    secsSince1900 = int.from_bytes(timeBuffer, "big")
    print('Total seconds since 1900: %d' % secsSince1900)
    # Get current time 2208988800 is the seconds between 1970 and 1900
    timeNow = time.gmtime(secsSince1900 - 2208988800)
    print(timeNow)

except KeyboardInterrupt:
    machine.reset()