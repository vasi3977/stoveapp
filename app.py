
from flask import Flask, render_template
import datetime
from ds18b20 import read_temp
import MAX6675 as MAX6675
from stepfor import stepfor, stepback
from flask_apscheduler import APScheduler
import RPi.GPIO as GPIO
import sqlite3

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

scheduler = APScheduler()
scheduler.start()

timpSneckArdere = 1.8

CSK = 21
CS = 20
DO = 16
sensor = MAX6675.MAX6675(CSK,CS,DO)


Temp = sensor.readTempC()
c = read_temp()



conn = sqlite3.connect("centrala.db", check_same_thread=False)
cursor = conn.cursor()



cursor.execute("SELECT * FROM datefunctionare ORDER BY data_pornire DESC LIMIT 1")
items = cursor.fetchall()
if (len(items) == 0):
	numarCurent = 0
else:
	for item in items:
		numarCurent = item[0]

def senzori():
	global Temp, c
	Temp = sensor.readTempC()
	c = read_temp()
	#print(Temp, " ", c)
	return "back"


scheduler.add_job(id="senzori", func = senzori, trigger = 'interval', seconds = 2)
#statusCentrala = 'OFF'


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
	datafinala = datetime.datetime.now()
	diferenta = datafinala - datainitiala

	url2 = "UPDATE datefunctionare SET data_oprire = '"+str(datafinala)+"', timp_functionare = '"+str(diferenta)+"' WHERE numar = " + str(numarCurent)
	cursor.execute(url2)

	conn.commit()
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "startSneckArdere" or job.name == "stopSneckArdere" or job.name == "pompaFinal"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id="startSneckArdere")
	#scheduler.remove_job(id="stopSneckArdere")
	pinOFF("ventilator")
	#scheduler.remove_job(id="pompaFinal")


def curatareFinal():
	global cursor, conn, numarCurent
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "curatareFinal"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id="curatareFinal")
	pinOFF("ventilator")
	scheduler.add_job(id="pompaFinal", func = pompaFinal, trigger = 'interval', seconds = 120)
	global statusCentrala
	statusCentrala = 'OFF'
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	url3 = "SELECT * FROM datefunctionare WHERE numar = "+str(numarCurent)
	cursor.execute(url3)
	conn.commit()
	items = cursor.fetchall()
	datainitiala = datetime.datetime.strptime(items[0][1], '%Y-%m-%d %H:%M:%S.%f')
	datafinala = datetime.datetime.now()
	diferenta = datafinala - datainitiala

	url2 = "UPDATE datefunctionare SET data_oprire = '"+str(datafinala)+"', timp_functionare = '"+str(diferenta)+"' WHERE numar = " + str(numarCurent)
	cursor.execute(url2)
	conn.commit()
	cursor.execute(url)
	conn.commit()
	print("curatareFinal")


def stopArdere():
	global cursor, conn
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "startSneckArdere" or job.name == "stopSneckArdere"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id="startSneckArdere")
	#scheduler.remove_job(id="stopSneckArdere")
	scheduler.add_job(id="curatareFinal", func = curatareFinal, trigger = 'interval', seconds = 350)
	pinOFF("sneck")
	global statusCentrala
	statusCentrala = 'Stop Ardere'
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	conn.commit()
	print("stopArdere")



def stopSneckArdere():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "stopSneckArdere"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id="stopSneckArdere")
	pinOFF("sneck")
	print("stopSneckArdere")


def startSneckArdere():
	print("startSneckArdere")
	global timpSneckArdere
	if(Temp < 30):
		jobs=scheduler.get_jobs()
		for job in jobs:
			if(job.name == "startSneckArdere" or job.name == "stopSneckArdere"):
				scheduler.remove_job(id = job.name)
		#scheduler.remove_job(id="startSneckArdere")
		#scheduler.remove_job(id="stopSneckArdere")
		eroare("Ardere")
	else:
		pinON("sneck")
		scheduler.add_job(id="stopSneckArdere", func = stopSneckArdere, trigger = 'interval', seconds = timpSneckArdere)
		print(timpSneckArdere)


def ardere():
	global cursor, conn
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "ventilatorAprindere" or job.name == "stopAprindere" or job.name == "rezistentaAprindere"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id="ventilatorAprindere")
	#scheduler.remove_job(id="stopAprindere")
	#scheduler.remove_job(id='rezistentaAprindere')
	global statusCentrala
	statusCentrala = 'Ardere'
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	conn.commit()
	url1 = "INSERT INTO datefunctionare VALUES (1, datetime('now'), datetime('now'), '')"
	cursor.execute(url2)
	conn.commit()
	pinON("pompa")
	pinON("ventilator")
	scheduler.add_job(id="startSneckArdere", func = startSneckArdere, trigger = 'interval', seconds = 12)
	print("Ardere")


def stopAprindere():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "ventilatorAprindere" or job.name == "stopAprindere" or job.name == "stareTemperaturaEvacuare"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id="stopAprindere")
	#scheduler.remove_job(id="ventilatorAprindere")
	#scheduler.remove_job(id="stareTemperaturaEvacuare")
	pinOFF("rezistenta")
	pinON("ventilator")
	stepback(1)
	eroare("aprindere")
	print("stopAprindere")

def perioadaStabil():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "perioadaStabil"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id="perioadaStabil")
	ardere()

def sneckStabilOff():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "sneckStabilOff" or job.name == "stopAprindere"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id="sneckStabilOff")
	#scheduler.remove_job(id="stopAprindere")
	pinOFF("sneck")
	print("sneckStabilOff")

def perioadaSneckStabil():
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "perioadaSneckStabil" or job.name == "stopAprindere"):
			scheduler.remove_job(id = job.name)
	#schedule.remove_job(id="perioadaSneckStabil")
	#scheduler.remove_job(id="stopAprindere")	
	pinON("sneck")
	scheduler.add_job(id="sneckStabilOff", func = sneckStabilOff, trigger = 'interval', seconds = 5)
	print("perioadaSneckStabil")
	

def stareTemperaturaEvacuare():
	print("stareTemperaturaEvacuare")
	global Temp, temperaturaInitialaAprindere, cursor, conn
	temperaturaEvacuare = Temp
	if (temperaturaEvacuare - temperaturaInitialaAprindere > 10):
		jobs=scheduler.get_jobs()
		for job in jobs:
			if(job.name == "stareTemperaturaEvacuare" or job.name == "stopAprindere" or job.name == "ventilatorAprindere" or job.name == "rezistentaAprindere"):
				scheduler.remove_job(id = job.name)
		#scheduler.remove_job(id="stareTemperaturaEvacuare")
		#scheduler.remove_job(id="stopAprindere")
		#scheduler.remove_job(id="ventilatorAprindere")
		#scheduler.remove_job(id='rezistentaAprindere')
		pinOFF("rezistenta")
		pinON("ventilator")
		stepback(1)
		global statusCentrala
		statusCentrala = "Stabil"
		url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
		cursor.execute(url)
		conn.commit()
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
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name == "rezistentaAprindere"):
			scheduler.remove_job(id = job.name)
	#scheduler.remove_job(id='rezistentaAprindere')
	scheduler.add_job(id = "ventilatorAprindere", func = ventilatorAprindere, trigger = 'interval', seconds = 8)
	print("rezistentaAprindere")


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
	stepfor(1)
	scheduler.add_job(id="rezistentaAprindere", func = rezistentaAprindere, trigger = 'interval', seconds = 120)
	scheduler.add_job(id="stareTemperaturaEvacuare", func = stareTemperaturaEvacuare, trigger = 'interval', seconds = 3)
	print("stopSneck")


def aprindere():
	global temperaturaInitialaAprindere, Temp, statusCentrala, cursor, conn, numarCurent
	numarCurent += 1
	temperaturaInitialaAprindere = Temp
	statusCentrala = 'Aprindere'
	url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
	cursor.execute(url)
	url2 = "INSERT INTO datefunctionare VALUES ("+ str(numarCurent) +", '"+str(datetime.datetime.now())+"', '"+str(datetime.datetime.now())+"', '')"
	cursor.execute(url2)
	conn.commit()
	pinON('sneck')
	pinOFF('rezistenta')
	scheduler.add_job(id="stopSneck", func = stopSneck, trigger = 'interval', seconds = 100)
	print("Aprindere")

def allJobsOff():
	global statusCentrala
	statusCentrala = 'OFF'
	jobs=scheduler.get_jobs()
	for job in jobs:
		if(job.name != "senzori"):
			scheduler.remove_job(id = job.name)
	#print(f[0].name)

cursor.execute("SELECT * FROM functionare")
items = cursor.fetchall()
for item in items:
	statusCentrala = item[1]
	if(statusCentrala == "Aprindere"):
		print("Aprindere")
		temperaturaInitialaAprindere = sensor.readTempC()
		stopSneck()
	elif(statusCentrala == "Stabil"):
		print("Stabil")
		pinOFF("rezistenta")
		pinON("ventilator")
		scheduler.add_job(id="perioadaStabil", func = perioadaStabil, trigger = 'interval', seconds = 120)
		scheduler.add_job(id="perioadaSneckStabil", func = perioadaSneckStabil, trigger = 'interval', seconds = 55)
	elif(statusCentrala == "Ardere"):
		print("Ardere")
		ardere()
	elif(statusCentrala == "Stop Ardere"):
		print("Stop Ardere")
		stopArdere()
	elif(statusCentrala == "Eroare Aprindere"):
		print("Eroare Aprindere")
		eroare("Aprindere")
	elif(statusCentrala == "Eroare Ardere"):
		print("Eroare Ardere")
		eroare("Ardere")



app = Flask(__name__)
pinOFF("ventilator")
pinOFF("sneck")
pinOFF("pompa")
pinOFF("rezistenta")


@app.route("/")
def index():
#	now = datetime.datetime.now()
#	timeString = now.strftime("%H:%M   %d/%m/%Y")
	global Temp, c, statusCentrala, timpSneckArdere
	templateData = {
#		'time': timeString,
		'tempEvacuare': Temp,
		'tempCentrala': c,
		'statusCentrala': statusCentrala,
		'timpSneckArdere': timpSneckArdere
	}
	return render_template('index.html', **templateData)


@app.route("/tempEvacuare")
def tempEvacuare():
	global Temp
	#Temp = sensor.readTempC()
	return str(Temp)


@app.route("/tempCentrala")
def tempCentrala():
	global c
	#c = read_temp()
	return str(c)

@app.route("/rezistentain")
def rezistentain():
	stepfor(1)
	return "for"

@app.route("/rezistentaout")
def rezistentaout():
	stepback(1)
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
	global statusCentrala, cursor, conn
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
	elif(statusCentralaParam == 6):
		global temperaturaInitialaAprindere
		temperaturaInitialaAprindere = sensor.readTempC()
		stopSneck()
	elif(statusCentralaParam == 7):
		eroare("Aprindere")
	elif(statusCentralaParam == 8):
		eroare("Ardere")
	elif(statusCentralaParam == 9):
		allJobsOff()
		statusCentrala = "OFF"
		url = "UPDATE functionare SET status = '"+ statusCentrala +"' WHERE nume = 'centrala'"
		cursor.execute(url)
		conn.commit()
	return "back"

@app.route("/startCentrala/<string:val>")
def startCentrala(val):
	global statusCentrala
	if (val == "START"):
		pass
	elif (val == "STOP"):
		pass


if __name__ == "__main__":
	app.run(debug=True)
