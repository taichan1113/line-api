import RPi.GPIO as GPIO
import time


# set GPIO mode
GPIO.setmode(GPIO.BCM)


# parameter
gpio_pump = 17

# setup GPIO
GPIO.setup(gpio_pump, GPIO.OUT)

# logic
GPIO.output(gpio_pump, 1)
time.sleep(5)
GPIO.output(gpio_pump, 0)
                            
# release GPIO
GPIO.cleanup(gpio_pump)