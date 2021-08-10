
from flask import Flask, render_template
import datetime
from ds18b20 import read_temp
import MAX6675 as MAX6675
from stepfor import stepfor, stepback
from flask_apscheduler import APScheduler
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


scheduler = APScheduler()
scheduler.start()
var = 5
contor = 1

timpSneckArdere = 1.8

CSK = 21
CS = 20
DO = 16
sensor = MAX6675.MAX6675(CSK,CS,DO)

Temp = sensor.readTempC()
c = read_temp()
statusCentrala = 'Aprindere'


ventilator = 6
sneck = 13
pompa = 19
rezistenta = 26
temperaturaInitialaAprindere = 0

GPIO.setup(ventilator, GPIO.OUT)
GPIO.setup(sneck, GPIO.OUT)
GPIO.setup(pompa, GPIO.OUT)
GPIO.setup(rezistenta, GPIO.OUT)


def pinOFF(par1):
	if(par1 == "ventilator"):
		GPIO.output(ventilator, GPIO.HIGH)
	elif(par1 == "sneck"):
		GPIO.output(sneck, GPIO.HIGH)
	elif(par1 == "pompa"):
		GPIO.output(pompa, GPIO.HIGH)
	elif(par1 == "rezistenta"):
		GPIO.output(rezistenta, GPIO.HIGH)



def pinON(par2):
	if(par2 == "ventilator"):
		GPIO.output(ventilator, GPIO.LOW)
	elif(par2 == "sneck"):
		GPIO.output(sneck, GPIO.LOW)
	elif(par2 == "pompa"):
		GPIO.output(pompa, GPIO.LOW)
	elif(par2 == "rezistenta"):
		GPIO.output(rezistenta, GPIO.LOW)

def pompaFinal():
	scheduler.remove_job(id="pompaFinal")
	pinOFF("pompa")
	print("pompaFinal")


def eroare(val):
	global statusCentrala
	statusCentrala = 'Eroare ' + val
	scheduler.remove_job(id="startSneckArdere")
	scheduler.remove_job(id="stopSneckArdere")
	pinOFF("ventilator")
	scheduler.remove_job(id="pompaFinal")


def curatareFinal():
	scheduler.remove_job(id="curatareFinal")
	pinOFF("ventilator")
	scheduler.add_job(id="pompaFinal", func = pompaFinal, trigger = 'interval', seconds = 120)
	global statusCentrala
	statusCentrala = 'OFF'
	print("curatareFinal")


def stopArdere():
	scheduler.remove_job(id="startSneckArdere")
	scheduler.remove_job(id="stopSneckArdere")
	scheduler.add_job(id="curatareFinal", func = curatareFinal, trigger = 'interval', seconds = 350)
	pinOFF("sneck")
	global statusCentrala
	statusCentrala = 'Stop Ardere'
	print("stopArdere")



def stopSneckArdere():
	scheduler.remove_job(id="stopSneckArdere")
	pinOFF("sneck")
	print("stopSneckArdere")


def startSneckArdere():
	print("startSneckArdere")
	global contor
	global timpSneckArdere
	if(contor == 0):
		scheduler.remove_job(id="startSneckArdere")
		scheduler.remove_job(id="stopSneckArdere")
		stopArdere()
	elif(Temp < 10):
		scheduler.remove_job(id="startSneckArdere")
		scheduler.remove_job(id="stopSneckArdere")
		eroare("Ardere")
	else:
		pinON("sneck")
		scheduler.add_job(id="stopSneckArdere", func = stopSneckArdere, trigger = 'interval', seconds = timpSneckArdere)
		print(timpSneckArdere)


def ardere():
	#scheduler.remove_job(id="ventilatorAprindere")
	#scheduler.remove_job(id="stopAprindere")
	#scheduler.remove_job(id='rezistentaAprindere')
	global statusCentrala
	statusCentrala = 'Ardere'
	pinON("pompa")
	pinON("ventilator")
	scheduler.add_job(id="startSneckArdere", func = startSneckArdere, trigger = 'interval', seconds = 12)
	print("Ardere")


def stopAprindere():
	scheduler.remove_job(id="stopAprindere")
	scheduler.remove_job(id="ventilatorAprindere")
	scheduler.remove_job(id="stareTemperaturaEvacuare")
	pinOFF("rezistenta")
	pinON("ventilator")
	eroare("aprindere")
	print("stopAprindere")

def perioadaStabil():
	scheduler.remove_job(id="perioadaStabil")
	ardere()

def sneckStabilOff():
	scheduler.remove_job(id="sneckStabilOff")
	scheduler.remove_job(id="stopAprindere")
	pinOFF("sneck")
	print("sneckStabilOff")

def perioadaSneckStabil():
	schedule.remove_job(id="perioadaSneckStabil")
	scheduler.remove_job(id="stopAprindere")	
	pinON("sneck")
	scheduler.add_job(id="sneckStabilOff", func = sneckStabilOff, trigger = 'interval', seconds = 5)
	print("perioadaSneckStabil")
	

def stareTemperaturaEvacuare():
	print("stareTemperaturaEvacuare")
	global Temp, temperaturaInitialaAprindere 
	temperaturaEvacuare = Temp
	if (temperaturaEvacuare - temperaturaInitialaAprindere > 10):
		scheduler.remove_job(id="stareTemperaturaEvacuare")
		scheduler.remove_job(id="stopAprindere")
		scheduler.remove_job(id="ventilatorAprindere")
		scheduler.remove_job(id='rezistentaAprindere')
		pinOFF("rezistenta")
		pinON("ventilator")
		global statusCentrala
		statusCentrala = "Stabil"
		scheduler.add_job(id="perioadaStabil", func = perioadaStabil, trigger = 'interval', seconds = 120)
		scheduler.add_job(id="perioadaSneckStabil", func = perioadaSneckStabil, trigger = 'interval', seconds = 55)


def ventilatorAprindere():
	print(GPIO.input(ventilator))
	if(GPIO.input(ventilator)):
		pinON("ventilator")
		print("ventilator OFF")
	else:
		pinOFF("ventilator")
		print("ventilator ON")


def rezistentaAprindere():
	scheduler.remove_job(id='rezistentaAprindere')
	scheduler.add_job(id = "ventilatorAprindere", func = ventilatorAprindere, trigger = 'interval', seconds = 8)
	print("rezistentaAprindere")


def stopSneck():
	global statusCentrala
	statusCentrala = 'Aprindere'
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "stopSneck"):
			scheduler.remove_job(id = job.name)
	pinOFF('sneck')
	scheduler.add_job(id="stopAprindere", func = stopAprindere, trigger = 'interval', seconds = 900)
	pinON('rezistenta')
	scheduler.add_job(id="rezistentaAprindere", func = rezistentaAprindere, trigger = 'interval', seconds = 120)
	scheduler.add_job(id="stareTemperaturaEvacuare", func = stareTemperaturaEvacuare, trigger = 'interval', seconds = 3)
	print("stopSneck")


def aprindere():
	global temperaturaInitialaAprindere, Temp, statusCentrala
	temperaturaInitialaAprindere = Temp
	statusCentrala = 'Aprindere'
	pinON('sneck')
	pinOFF('rezistenta')
	scheduler.add_job(id="stopSneck", func = stopSneck, trigger = 'interval', seconds = 100)
	print("Aprindere")

def allJobsOff():
	jobs=scheduler.get_jobs()
	for job in jobs:
		scheduler.remove_job(id = job.name)
	#print(f[0].name)


app = Flask(__name__)
pinOFF("ventilator")
pinOFF("sneck")
pinOFF("pompa")
pinOFF("rezistenta")


@app.route("/")
def index():
	now = datetime.datetime.now()
	timeString = now.strftime("%H:%M   %d/%m/%Y")
	templateData = {
		'time': timeString,
		'tempEvacuare': Temp,
		'tempCentrala': c,
		'statusCentrala': statusCentrala,
		'timpSneckArdere': timpSneckArdere
	}
	return render_template('index.html', **templateData)


@app.route("/tempEvacuare")
def tempEvacuare():
	global Temp
	Temp = sensor.readTempC()
	return str(Temp)


@app.route("/tempCentrala")
def tempCentrala():
	global c
	c = read_temp()
	return str(c)

@app.route("/rezistentain")
def rezistentain():
	stepfor()
	return "for"

@app.route("/rezistentaout")
def rezistentaout():
	stepback()
	return "back"


@app.route("/pin/<string:pin_id>/<string:val>")
def pin(pin_id, val):
	if(val=="ON"):
		pinON(pin_id)
		print(pin_id + " ON")
	elif(val=="OFF"):
		pinOFF(pin_id)
		print(pin_id + " OFF")
	return "back"

@app.route("/sneckTimpArdere/<float:timpArdere>")
def setareSneckTimpArdere(timpArdere):
	global timpSneckArdere
	timpSneckArdere = timpArdere
	return "back"

@app.route("/timpSneckArdere")
def sneckTimpArdereFunc():
	global timpSneckArdere 
	return str(timpSneckArdere)

@app.route("/statusCentrala")
def statusCentralaFunc():
	global statusCentrala
	return statusCentrala

@app.route("/statusCentrala/<int:statusCentralaParam>")
def statusCentralaParamFunc(statusCentralaParam):
	global statusCentrala
	if(statusCentralaParam == 0):
		statusCentrala = "OFF"
	elif(statusCentralaParam == 1):
		aprindere()
	elif(statusCentralaParam == 2):
		pinOFF("rezistenta")
		pinON("ventilator")
		scheduler.add_job(id="perioadaStabil", func = perioadaStabil, trigger = 'interval', seconds = 120)
		scheduler.add_job(id="perioadaSneckStabil", func = perioadaSneckStabil, trigger = 'interval', seconds = 55)
	elif(statusCentralaParam == 3):
		ardere()
	elif(statusCentralaParam == 4):
		stopArdere()
	elif(statusCentralaParam == 6):
		stopSneck()
	elif(statusCentralaParam == 7):
		eroare("Aprindere")
	elif(statusCentralaParam == 8):
		eroare("Ardere")
	elif(statusCentralaParam == 9):
		allJobsOff()
	return "back"



if __name__ == "__main__":
	app.run(debug=True)
