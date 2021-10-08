import datetime

weekday = int(datetime.datetime.now().strftime("%w"))
hour = int(datetime.datetime.now().strftime("%H"))
minute = int(datetime.datetime.now().strftime("%M"))

print(weekday, hour, minute)
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

print('start: ', startTemperatura)
print('stop: ', stopTemperatura)