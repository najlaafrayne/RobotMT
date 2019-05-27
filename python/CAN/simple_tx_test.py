#!/usr/bin/python3
#
# simple_tx_test.py
# 
# This python3 sent CAN messages out, with byte 7 increamenting each time.
# For use with CAN SPI CLICK on the Raspberry Pi
#
# 02-05-19 MASSOURI ABDELFATTAH
#
#
#


import RPi.GPIO as GPIO
import can
import time
import os


led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)

count = 0

print('\n\rCAN Rx test')
print('Bring up CAN0....')

# Bring up can0 interface at 500kbps
os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
time.sleep(0.1)	
print('Press CTL-C to exit')

try:
	bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
except OSError:
	print('Cannot find CAN SPI CLICK.')
	GPIO.output(led,False)
	exit()

# Main loop
try:
	while True:
		GPIO.output(led,True)	
		#Message to be sent (id and data)
		#msg = can.Message(arbitration_id=0x7de,data=[0x00,0x01,0x02, 0x03, 0x04, 0x05,0x06, count & 0xff],extended_id=False)
		msg = can.Message(arbitration_id=0x249C490,data=[0xff,0xf, 0xff, 0,0,0,0,0],extended_id=True)
		bus.send(msg)
		count +=1
		#time.sleep(0.1)
		GPIO.output(led,False)
		time.sleep(0.1)	
		print(count)	
		 

	
except KeyboardInterrupt:
	#Catch keyboard interrupt
	GPIO.output(led,False)
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')	