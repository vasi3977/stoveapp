import os
import smtplib
from requests import get

EMAIL_ADRESS = 'vasile03.stan@gmail.com'
EMAIL_PASSWORD = 'Vasile3#!'

ip = get('https://api.ipify.org').text
print('My public IP address is: {}'.format(ip))

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
	smtp.ehlo()
	smtp.starttls()
	smtp.ehlo()

	smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)

	subject = "Adresa de ip"
	body = 'My public IP address is: ' + ip

	msg = f'Subject: {subject}\n\n{body}'

	smtp.sendmail(EMAIL_ADRESS, 'vasile.stan@gmail.com', msg)