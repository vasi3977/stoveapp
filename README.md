# stoveapp
webserver for pellet stove with raspberry pi zero w

This app works in the pellet stove installed in my home. From 2019 I have heat from sep/oct till apr/may with this application.
The python flask web server runs on a raspberry pi zero w module, 2 MAX6675 sensors, 1 ultrasonic sensor HC-SR04+, 1 stepper motor Nema 17, driver DRV8825,
2 AC-DC 230V to 12 V transformers, solid state relay with 4 relays.
I made this app because my initial pelet stove control board has been damaged by a short and I told myself I can do it.

The pellets ignite from an incandescent spark plug witch is inserted and removed by NEMA 17 stepper motor.
The Nema 17 stepper motor is the newest module in the project because 5 spark plugs were destroyed standing in the fire, so I had to do something to pull out the spark plug
from fire.

Obviously the app will be improved in terms of clean coding etc.
