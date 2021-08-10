import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)



class centrala:

	ventilator = 6,
	sneck = 13,
	pompa = 19,
	rezistenta = 26

	GPIO.setup(ventilator, GPIO.OUT)
	GPIO.setup(sneck, GPIO.OUT)
	GPIO.setup(pompa, GPIO.OUT)
	GPIO.setup(rezistenta, GPIO.OUT)


	def pinON(par1):
		if(par1 == "ventilator"):
			GPIO.output(ventilator, GPIO.HIGH)
		elif(par1 == "sneck"):
			GPIO.output(sneck, GPIO.HIGH)
		elif(par1 == "pompa"):
			GPIO.output(pompa, GPIO.HIGH)
		elif(par1 == "rezistenta"):
			GPIO.output(rezistenta, GPIO.HIGH)


	def pinOFF(par2):
		if(par2 == "ventilator"):
			GPIO.output(ventilator, GPIO.LOW)
		elif(par2 == "sneck"):
			GPIO.output(sneck, GPIO.LOW)
		elif(par2 == "pompa"):
			GPIO.output(pompa, GPIO.LOW)
		elif(par2 == "rezistenta"):
			GPIO.output(rezistenta, GPIO.LOW)

	
	