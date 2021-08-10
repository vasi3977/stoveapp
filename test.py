import requests
import time

BASE = "http://127.0.0.1:5000"

for i in range(5):
	response = requests.get(BASE + "/temp")
	print(response.json())
	time.sleep(1)
