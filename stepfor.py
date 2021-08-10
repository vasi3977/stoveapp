import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
control_pins = [23,17,27,22]


def stepfor():
	for pin in control_pins:
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, 0)
		halfstep_seq = [
			[1,0,0,0],
			[1,1,0,0],
			[0,1,0,0],
			[0,1,1,0],
			[0,0,1,0],
  			[0,0,1,1],
  			[0,0,0,1],
  			[1,0,0,1]
			]
	for i in range(2):
		for i in range(512):
			for halfstep in range(8):
				for pin in range(4):
					GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
				time.sleep(0.001)
	


def stepback():
	for pin in control_pins:
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, 0)
		halfstep_seq = [
			[1,0,0,0],
			[1,1,0,0],
			[0,1,0,0],
			[0,1,1,0],
			[0,0,1,0],
  			[0,0,1,1],
  			[0,0,0,1],
  			[1,0,0,1]
			]
	for i in range(2):
		for i in range(512):
			for halfstep in reversed(range(8)):
				for pin in range(4):
					GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
				time.sleep(0.001)
	