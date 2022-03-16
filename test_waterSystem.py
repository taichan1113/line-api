import time
import subprocess
import RPi.GPIO as GPIO
from gpiozero import MCP3008

from run_pump import runPump
from show_humidity import humidityPercentage

if __name__ == "__main__":
    # setup pump
    GPIO.setmode(GPIO.BCM)
    gpio_pump = 17

    # setup humidity
    sensor = MCP3008(channel = 0)

    try:
        while True:
            hum = humidityPercentage(sensor, Vref=3.3, dry=290, water=130)
            if hum < 80:
                runPump(3, gpio_pump)
            
            time.sleep(3)
                
    except: KeyboardInterrupt
    subprocess.call('clear')
