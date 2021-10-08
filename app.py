from flask import Flask, render_template
import datetime
#from ds18b20 import read_temp
import MAX6675 as MAX6675
from distance import distance
from flask_apscheduler import APScheduler
import RPi.GPIO as GPIO
import sqlite3
import os
import smtplib
import time
from requests import get
from motor3 import moveRezistenta
import psutil





ventilator = 6
sneck = 13
pompa = 19
rezistenta = 26
temperaturaInitialaAprindere = 0

stareVentilator = "OFF"
stareSneck = "OFF"
starePompa = "OFF"
stareRezistenta = "OFF"
statusRezistenta = "OUT"


GPIO.setup(ventilator, GPIO.OUT)
GPIO.setup(sneck, GPIO.OUT)
GPIO.setup(pompa, GPIO.OUT)
GPIO.setup(rezistenta, GPIO.OUT)
GPIO.output(ventilator, GPIO.HIGH)
GPIO.output(sneck, GPIO.HIGH)
GPIO.output(pompa, GPIO.HIGH)
GPIO.output(rezistenta, GPIO.HIGH)

scheduler = APScheduler()
scheduler.start()


CSK = 21
CS = 20
DO = 16

CSK2 = 7
CS2= 11
DO2 = 12
sensor = MAX6675.MAX6675(CSK,CS,DO)
sensor1 = MAX6675.MAX6675(CSK2,CS2,DO2)

cont = 0

#dist = round(distance())
dist = 11
Temp = sensor.readTempC()
time.sleep(0.5)

Temp2 = sensor1.readTempC()
#c = read_temp()



conn = sqlite3.connect("centrala.db", check_same_thread=False)
cursor = conn.cursor()



cursor.execute("SELECT * FROM datefunctionare")
items = cursor.fetchall()
numarCurent = len(items)

def temperaturaLiving():
	global tempLiving
	temperature = get('http://192.168.1.137:5555/temperature').text
	tempLiving = float(temperature)
	return tempLiving

tempLiving = temperaturaLiving()

def senzori():
	global Temp, Temp2, dist, cont
	Temp = round(sensor.readTempC(), 1)
	time.sleep(0.3)
#	c = round(read_temp(), 1)
#	dist = round(distance())
	Temp2 = round(sensor1.readTempC(), 1)

	if (Temp2 > 40):
		if (cont == 0):
			pinON("pompa")
			cont = 1
	else:
		if (cont == 1):
			pinOFF("pompa")
			cont = 0

	return "back"

def sendMail():
	EMAIL_ADRESS = 'vasile03.stan@gmail.com'
	EMAIL_PASSWORD = 'Vasile3#!'

	ip = get('https://api.ipify.org').text

	with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()
		smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)
		subject = "Adresa de ip"
		body = 'My public IP address is: ' + ip
		msg = f'Subject: {subject}\n\n{body}'
		smtp.sendmail(EMAIL_ADRESS, 'vasile.stan@gmail.com', msg)

def sendMailPornire():
	EMAIL_ADRESS = 'vasile03.stan@gmail.com'
	EMAIL_PASSWORD = 'Vasile3#!'

	with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()
		smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)
		subject = "Pornire raspberry"
		body = 'Pornire Raspberry PI ZERO W'
		msg = f'Subject: {subject}\n\n{body}'
		smtp.sendmail(EMAIL_ADRESS, 'vasile.stan@gmail.com', msg)


sendMailPornire()

jobs=scheduler.get_jobs()
for job in jobs:
	if(job.name == "senzori"):
		scheduler.remove_job(id = job.name)
scheduler.add_job(id="senzori", func = senzori, trigger = 'interval', seconds = 5, max_instances=5)

scheduler.add_job(id="temperaturaLiving", func = temperaturaLiving, trigger = 'interval', seconds = 5, max_instances=5)

scheduler.add_job(id="mail", func = sendMail, trigger = 'interval', seconds = 21600, max_instances=5)

def triggerRezist(ind):
	global statusRezistenta
	scheduler.remove_job("senzori")
	scheduler.remove_job("temperaturaLiving")
	scheduler.remove_job("statusCentralaMonitor")
	moveRezistenta(2, 1.8, 6, ind, 100)
	scheduler.add_job(id="senzori", func = senzori, trigger = 'interval', seconds = 5, max_instances=5)
	scheduler.add_job(id="temperaturaLiving", func = temperaturaLiving, trigger = 'interval', seconds = 5, max_instances=5)
	scheduler.add_job(id="statusCentralaMonitor", func = statusCentralaMonitor, trigger = 'interval', seconds = 2, max_instances=5)
	if(ind == 1):
		statusRezistenta = "IN"
	else:
		statusRezistenta = "OUT"

def pinOFF(par1):
	global stareVentilator, stareSneck, starePompa, stareRezistenta
	if(par1 == "ventilator"):
		GPIO.output(ventilator, GPIO.HIGH)
		stareVentilator = "OFF"
	elif(par1 == "sneck"):
		GPIO.output(sneck, GPIO.HIGH)
		stareSneck = "OFF"
	elif(par1 == "pompa"):
		GPIO.output(pompa, GPIO.HIGH)
		cont = 0
		starePompa = "OFF"
	elif(par1 == "rezistenta"):
		GPIO.output(rezistenta, GPIO.HIGH)
		stareRezistenta = "OFF"



def pinON(par2):
	global stareVentilator, stareSneck, starePompa, stareRezistenta
	if(par2 == "ventilator"):
		GPIO.output(ventilator, GPIO.LOW)
		stareVentilator = "ON"
	elif(par2 == "sneck"):
		GPIO.output(sneck, GPIO.LOW)
		stareSneck = "ON"
	elif(par2 == "pompa"):
		GPIO.output(pompa, GPIO.LOW)
		cont = 1
		starePompa = "ON"
	elif(par2 == "rezistenta"):
		GPIO.output(rezistenta, GPIO.LOW)
		stareRezistenta = "ON"

def pompaFinal():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "pompaFinal"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id="pompaFinal")
	pinOFF("pompa")
	print("pompaFinal")

def eroare(val):
	global cursor, conn
	global statusCentrala
	statusCentrala = 'Eroare ' + val
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	conn.commit()
	url3 = "SELECT * FROM datefunctionare WHERE numar = "+str(numarCurent)
	cursor.execute(url3)
	conn.commit()
	items = cursor.fetchall()
	datainitiala = datetime.datetime.strptime(items[0][1], '%Y-%m-%d %H:%M:%S.%f')
	datafinala = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
	diferenta = datafinala - datainitiala
	if(val == "Ardere"):
		url2 = "UPDATE datefunctionare SET data_oprire = '"+str(datafinala)+"', timp_functionare = '"+str(diferenta)+"' WHERE numar = " + str(numarCurent)
		cursor.execute(url2)
		conn.commit()
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "startSneckArdere" or job.name == "stopSneckArdere"):
			scheduler.remove_job(id = job.name)
	pinOFF("ventilator")


def curatareFinal():
	global cursor, conn, numarCurent
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "curatareFinal"):
			scheduler.remove_job(id = job.name)
	pinOFF("ventilator")
#	scheduler.add_job(id="pompaFinal", func = pompaFinal, trigger = 'interval', seconds = 120)
	global statusCentrala
	statusCentrala = 'OFF'
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	url3 = "SELECT * FROM datefunctionare WHERE numar = "+str(numarCurent)
	cursor.execute(url3)
	items = cursor.fetchall()
	datainitiala = datetime.datetime.strptime(items[0][1], '%d/%m/%Y, %H:%M:%S')
	datafinalaTemp = datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
	datafinala = datetime.datetime.strptime(datafinalaTemp, '%d/%m/%Y, %H:%M:%S')
	diferenta = datafinala - datainitiala

	url2 = "UPDATE datefunctionare SET data_oprire = '"+datafinalaTemp+"', timp_functionare = '"+str(diferenta)+"' WHERE numar = " + str(numarCurent)
	cursor.execute(url2)
	conn.commit()
	cursor.execute(url)
	conn.commit()


def stopArdere():
	global cursor, conn
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "startSneckArdere" or job.name == "stopSneckArdere"):
			scheduler.remove_job(id = job.name)
	scheduler.add_job(id="curatareFinal", func = curatareFinal, trigger = 'interval', seconds = 350)
	pinOFF("sneck")
	global statusCentrala
	statusCentrala = 'Stop Ardere'
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	conn.commit()


def stopSneckArdere():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "stopSneckArdere"):
			scheduler.remove_job(id = job.name)
	pinOFF("sneck")


def startSneckArdere():
	global timpSneckArdere
	if(Temp < 30):
		jobs=scheduler.get_jobs()
		for job in jobs:
			if(job.name == "startSneckArdere" or job.name == "stopSneckArdere"):
				scheduler.remove_job(id = job.name)
		eroare("Ardere")
	else:
		pinON("sneck")
		scheduler.add_job(id="stopSneckArdere", func = stopSneckArdere, trigger = 'interval', seconds = timpSneckArdere)


def ardere():
	global cursor, conn
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "ventilatorAprindere" or job.name == "stopAprindere" or job.name == "rezistentaAprindere"):
			scheduler.remove_job(id = job.name)
	global statusCentrala
	statusCentrala = 'Ardere'
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	conn.commit()
	pinON("ventilator")
#	pinON("pompa")
	scheduler.add_job(id="startSneckArdere", func = startSneckArdere, trigger = 'interval', seconds = 12)


def stopAprindere():
	triggerRezist(0)
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "ventilatorAprindere" or job.name == "stopAprindere" or job.name == "stareTemperaturaEvacuare"):
			scheduler.remove_job(id = job.name)
	pinOFF("rezistenta")
	pinON("ventilator")
	eroare("aprindere")

def perioadaStabil():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "perioadaStabil"):
			scheduler.remove_job(id = job.name)
	ardere()

def sneckStabilOff():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "sneckStabilOff" or job.name == "stopAprindere"):
			scheduler.remove_job(id = job.name)
	pinOFF("sneck")

def perioadaSneckStabil():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "perioadaSneckStabil" or job.name == "stopAprindere"):
			scheduler.remove_job(id = job.name)	
	pinON("sneck")
	scheduler.add_job(id="sneckStabilOff", func = sneckStabilOff, trigger = 'interval', seconds = 5)
	

def stareTemperaturaEvacuare():
	print("stareTemperaturaEvacuare")
	global Temp, temperaturaInitialaAprindere, cursor, conn, statusCentrala
	temperaturaEvacuare = Temp
	if (temperaturaEvacuare - temperaturaInitialaAprindere > 10):
		triggerRezist(0)
		jobs=scheduler.get_jobs()
		for job in jobs:
			if(job.name == "stareTemperaturaEvacuare" or job.name == "stopAprindere" or job.name == "ventilatorAprindere" or job.name == "rezistentaAprindere"):
				scheduler.remove_job(id = job.name)
		pinOFF("rezistenta")
		pinON("ventilator")

		statusCentrala = "Stabil"
		url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
		cursor.execute(url)
		conn.commit()
		scheduler.add_job(id="perioadaStabil", func = perioadaStabil, trigger = 'interval', seconds = 150)
		scheduler.add_job(id="perioadaSneckStabil", func = perioadaSneckStabil, trigger = 'interval', seconds = 55)


def ventilatorAprindere():
	print(GPIO.input(ventilator))
	if(GPIO.input(ventilator)):
		pinON("ventilator")
	else:
		pinOFF("ventilator")


def rezistentaAprindere():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "rezistentaAprindere"):
			scheduler.remove_job(id = job.name)
	scheduler.add_job(id = "ventilatorAprindere", func = ventilatorAprindere, trigger = 'interval', seconds = 8)


def stopSneck():
	global statusCentrala, cursor, conn
	statusCentrala = 'Aprindere'
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	conn.commit()
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "stopSneck"):
			scheduler.remove_job(id = job.name)
	pinOFF('sneck')
	scheduler.add_job(id="stopAprindere", func = stopAprindere, trigger = 'interval', seconds = 900)
	pinON('rezistenta')
	scheduler.add_job(id="rezistentaAprindere", func = rezistentaAprindere, trigger = 'interval', seconds = 100)
	scheduler.add_job(id="stareTemperaturaEvacuare", func = stareTemperaturaEvacuare, trigger = 'interval', seconds = 3)


def aprindere():
	triggerRezist(1)

	global temperaturaInitialaAprindere, Temp, statusCentrala, cursor, conn, numarCurent
	temperaturaInitialaAprindere = Temp
	statusCentrala = 'Aprindere'
	numarCurent += 1
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	url2 = "INSERT INTO datefunctionare VALUES ("+ str(numarCurent) +", '"+str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))+"', '"+""+"', '')"
	cursor.execute(url2)
	conn.commit()
	pinON('sneck')
	pinOFF('rezistenta')
	scheduler.add_job(id="stopSneck", func = stopSneck, trigger = 'interval', seconds = 120)


def allJobsOff():
	global statusCentrala
	statusCentrala = 'OFF'
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name != "senzori" or job.name != "mail" or job.name !="temperaturaLiving" or job.name != "statusCentralaMonitor"):
			scheduler.remove_job(id = job.name)


def programCentralaMonitorFunctionare(program):
	global startTemperatura, stopTemperatura
	weekday = int(datetime.datetime.now().strftime("%w"))
	hour = int(datetime.datetime.now().strftime("%H"))
	minute = int(datetime.datetime.now().strftime("%M"))
	if(program == "PROG"):	
		if(1<= weekday and weekday <=5):
			if((22 > hour and hour >= 17) or (8 > hour and hour >= 6)):
				startTemperatura = 21.0
				stopTemperatura = 22.0
			elif(24 < hour or hour <= 6):
				startTemperatura = 19.5
				stopTemperatura = 20.5
			else:
				startTemperatura = 20.5
				stopTemperatura = 21.5
		elif(23 > hour and hour >= 8):
			startTemperatura = 21.0
			stopTemperatura = 22.0
		else:
			startTemperatura = 19.5
			stopTemperatura = 20.5
	if(program == "PROG1"):
		startTemperatura = 21
		stopTemperatura = 22
	if(program == "PROG2"):
		startTemperatura = 21.5
		stopTemperatura = 22.5
	if(program == "PROG3"):
		startTemperatura = 20.5
		stopTemperatura = 21.5
	if(program == "FIX"):
		if(1<= weekday and weekday <=5):
			if(hour == 6):
				startTemperatura = 21.0
				stopTemperatura = 22.0
			elif(hour == 17):
				startTemperatura = 21.0
				stopTemperatura = 22.0
			elif(hour == 20):
				startTemperatura = 21.0
				stopTemperatura = 22.0
			else:
				startTemperatura = 20.0
				stopTemperatura = 21.0
		else:
			if(hour == 6):
				startTemperatura = 21.0
				stopTemperatura = 22.0
			elif(hour == 17):
				startTemperatura = 21.0
				stopTemperatura = 22.0
			elif(hour == 20):
				startTemperatura = 21.0
				stopTemperatura = 22.0
			else:
				startTemperatura = 20.0
				stopTemperatura = 21.0

	if(program == "FIX2"):
		if(1<= weekday and weekday <=5):
			if(hour == 6 and minute >= 1):
				startTemperatura = 21.5
				stopTemperatura = 22.5
			elif(hour == 17 and minute >= 1):
				startTemperatura = 21.5
				stopTemperatura = 22.5
			elif(hour == 20 and minute >= 1):
				startTemperatura = 21.5
				stopTemperatura = 22.5
			else:
				startTemperatura = 20.5
				stopTemperatura = 21.5
		else:
			if(hour == 7 and minute >= 1):
				startTemperatura = 21.5
				stopTemperatura = 22.5
			elif(hour == 17 and minute >= 1):
				startTemperatura = 21.5
				stopTemperatura = 22.5
			elif(hour == 20 and minute >= 1):
				startTemperatura = 21.5
				stopTemperatura = 22.5
			else:
				startTemperatura = 20.5
				stopTemperatura = 21.5


	if(program == "AER"):
		startTemperatura = 11
		stopTemperatura = 12
	if(program == "CALD"):
		startTemperatura = 27
		stopTemperatura = 28

def statusCentralaMonitor():
	global tempLiving, startTemperatura, stopTemperatura
	programCentralaMonitorFunctionare(statusProgram)
	if(tempLiving < startTemperatura):
		if(statusCentrala == "OFF"):
			aprindere()
	if(tempLiving > stopTemperatura):
		if(statusCentrala == "Ardere"):
			stopArdere()

scheduler.add_job(id="statusCentralaMonitor", func = statusCentralaMonitor, trigger = 'interval', seconds = 3, max_instances=5)


cursor.execute("SELECT * FROM functionare")
items = cursor.fetchall()
for item in items:
	statusCentrala = item[1]
	timpSneckArdere = item[2]
	stareCentrala = item[3]
	statusProgram = item[4]
	programCentralaMonitorFunctionare(statusProgram)
	if(statusCentrala == "Aprindere"):
		temperaturaInitialaAprindere = sensor.readTempC()
		stopSneck()
	elif(statusCentrala == "Stabil"):
		pinOFF("rezistenta")
		pinON("ventilator")
		scheduler.add_job(id="perioadaStabil", func = perioadaStabil, trigger = 'interval', seconds = 120)
		scheduler.add_job(id="perioadaSneckStabil", func = perioadaSneckStabil, trigger = 'interval', seconds = 55)
	elif(statusCentrala == "Ardere"):
		ardere()
	elif(statusCentrala == "Stop Ardere"):
		stopArdere()
	elif(statusCentrala == "Eroare Aprindere"):
		eroare("Aprindere")
	elif(statusCentrala == "Eroare Ardere"):
		eroare("Ardere")
	


app = Flask(__name__)
pinOFF("ventilator")
pinOFF("sneck")
pinOFF("pompa")
pinOFF("rezistenta")


@app.route("/centrala")
def index():
	global Temp, Temp2, statusCentrala, timpSneckArdere, stareVentilator, stareSneck, starePompa, stareRezistenta, statusRezistenta
	templateData = {
		'dist': dist,
		'tempEvacuare': Temp,
		'tempCentrala': Temp2,
		'statusCentrala': statusCentrala,
		'timpSneckArdere': timpSneckArdere,
		'stareVentilator': stareVentilator,
		'stareSneck': stareSneck,
		'starePompa': starePompa,
		'stareRezistenta': stareRezistenta,
		'statusRezistenta': statusRezistenta
	}
	return render_template('index.html', **templateData)

@app.route("/")
def programCentrala():
	global tempLiving, statusProgram, startTemperatura, stopTemperatura
	templateData = {
		'tempLiving': tempLiving,
		'statusProgram': statusProgram,
		'startTemperatura': startTemperatura,
		'stopTemperatura': stopTemperatura
	}
	return render_template('programCentrala.html', **templateData)

@app.route("/dateFunctionare")
def dateFunctionare():
	global cursor
	cursor.execute("SELECT * FROM datefunctionare")
	items = cursor.fetchall()
	items = reversed(items)
	templateData = {
		'items': items
		}
	return render_template('bazaDate.html', **templateData)



@app.route("/programCentrala/statusProgram")
def statusProgramRefresh():
	global statusProgram
	return str(statusProgram)
	

@app.route("/programCentrala/startTemperatura")
def startTemperaturaRefresh():
	global startTemperatura
	return str(startTemperatura)

@app.route("/programCentrala/stopTemperatura")
def stopTemperaturaRefresh():
	global stopTemperatura
	return str(stopTemperatura)


@app.route("/tempEvacuare")
def tempEvacuare():
	global Temp
	return str(Temp)


@app.route("/tempCentrala")
def tempCentrala():
	global Temp2
	return str(Temp2)

@app.route("/distance")
def distPeleti():
	global dist
#	dist = round(distance())
	return str(11)


@app.route("/rezistentain")
def rezistentain():
#	for p in psutil.process_iter(attrs=['pid', 'name']):
#		if "flask" in (p.info['name']).lower():
#			print("yes", (p.info['pid']))
#	p = psutil.Process(p.info['pid'])
#	p.suspend()
	triggerRezist(1)
#	p.resume()
	return "IN"

@app.route("/rezistentaout")
def rezistentaout():
#	for p in psutil.process_iter(attrs=['pid', 'name']):
#		if "flask" in (p.info['name']).lower():
#			print("yes", (p.info['pid']))
#	p = psutil.Process(p.info['pid'])
#	p.suspend()
	triggerRezist(0)
#	p.resume()

	return "OUT"


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
	url = "UPDATE functionare SET tsneck = '"+ str(timpSneckArdere) +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	conn.commit()
	return "back"

@app.route("/timpSneckArdere")
def sneckTimpArdereFunc():
	global timpSneckArdere 
	return str(timpSneckArdere)

@app.route("/programCentrala/tempLiving")
def tempLivingProgramCentrala():
	global tempLiving 
	return str(tempLiving)


@app.route("/statusCentrala")
def statusCentralaFunc():
	global statusCentrala
	return statusCentrala

@app.route("/statusCentrala/stareVentilator")
def statusCentralaStareVentilator():
	global stareVentilator
	return stareVentilator

@app.route("/statusCentrala/stareSneck")
def statusCentralaStareSneck():
	global stareSneck
	return stareSneck

@app.route("/statusCentrala/starePompa")
def statusCentralaStarePompa():
	global starePompa
	return starePompa

@app.route("/statusCentrala/stareRezistenta")
def statusCentralaStareRezistenta():
	global stareRezistenta
	return stareRezistenta

@app.route("/statusCentrala/statusRezistenta")
def statusCentralaStareRezistentaMove():
	global statusRezistenta
	return statusRezistenta


@app.route("/programCentrala/setareProgram/<string:program>")
def setareProgramCentrala(program):
	global statusProgram
	statusProgram = program
	programCentralaMonitorFunctionare(statusProgram)
	url = "UPDATE functionare SET program = '"+ statusProgram +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	conn.commit()
	return "back"

	
@app.route("/statusCentrala/<int:statusCentralaParam>")
def statusCentralaParamFunc(statusCentralaParam):
	global statusCentrala, cursor, conn, temperaturaInitialaAprindere
	if(statusCentralaParam == 0):
		statusCentrala = "OFF"
		url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
		cursor.execute(url)
		conn.commit()
	elif(statusCentralaParam == 1):
		aprindere()
	elif(statusCentralaParam == 2):
		statusCentrala = "Stabil"
		url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
		cursor.execute(url)
		conn.commit()
		pinOFF("rezistenta")
		pinON("ventilator")
		scheduler.add_job(id="perioadaStabil", func = perioadaStabil, trigger = 'interval', seconds = 120)
		scheduler.add_job(id="perioadaSneckStabil", func = perioadaSneckStabil, trigger = 'interval', seconds = 55)
	elif(statusCentralaParam == 3):
		ardere()
	elif(statusCentralaParam == 4):
		stopArdere()
	elif(statusCentralaParam == 11):
		stopArdere()
		k = 0
		jobs=scheduler.get_jobs()
		for job in jobs:
			if(job.name == "statusCentralaMonitor"):
				k = 1
		if(k == 0):
			scheduler.add_job(id="statusCentralaMonitor", func = statusCentralaMonitor, trigger = 'interval', seconds = 3, max_instances=5)

	elif(statusCentralaParam == 6):
		temperaturaInitialaAprindere = sensor.readTempC()
		stopSneck()
	elif(statusCentralaParam == 7):
		eroare("Aprindere")
	elif(statusCentralaParam == 8):
		eroare("Ardere")
	elif(statusCentralaParam == 10):
		jobs=scheduler.get_jobs()
		for job in jobs:
			if(job.name == "statusCentralaMonitor"):
				scheduler.remove_job(id = job.name)
		aprindere()

	elif(statusCentralaParam == 9):
		allJobsOff()
		statusCentrala = "OFF"
		url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
		cursor.execute(url)
		conn.commit()
	return "back"



#@app.route("/startCentrala/<string:val>")
#def startCentrala(val):
#	global stareCentrala
#	if (val == "START"):
#		stareCentrala = 1
#		url = "UPDATE functionare SET scentral = '"+ str(stareCentrala) +"' WHERE nume = 'centrala'"
#		cursor.execute(url)
#		conn.commit()
#		#aprindere()
#	elif (val == "STOP"):
#		stareCentrala = 0 
#		url = "UPDATE functionare SET scentral = '"+ str(stareCentrala) +"' WHERE nume = 'centrala'"
#		cursor.execute(url)
#		conn.commit()
#	return "back"


@app.route("/bazaDate")
def programBaza():
	global tempLiving, statusProgram, startTemperatura, stopTemperatura
	templateData = {
		'tempLiving': tempLiving,
		'statusProgram': statusProgram,
		'startTemperatura': startTemperatura,
		'stopTemperatura': stopTemperatura
	}
	return render_template('bazaDate.html', **templateData)

