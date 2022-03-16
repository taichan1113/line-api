import RPi.GPIO as GPIO
import time
from DHT11_Python import dht11

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

sensor = dht11.DHT11(pin=14)

try:
	while True:
	    result = sensor.read()
	    if result.is_valid():
	        print("Temperature: %-3.1f C" % result.temperature)
	        print("Humidity: %-3.1f %%" % result.humidity)

	    time.sleep(1)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()