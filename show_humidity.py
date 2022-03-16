import time
import subprocess
from gpiozero import MCP3008

Vref = 3.3
dry = 290 # sensor max 283
water = 130 # sensor min 133
senV1p2 = MCP3008(channel=0)

def humidityPercentage(sensor, Vref, dry, water):
    hum = round(sensor.value * Vref * 100, 1)
    return (1 - (hum - water) / (dry - water)) * 100

if __name__ == "__main__":
    try:
        while True:
            hum = humidityPercentage(senV1p2, Vref, dry, water)
            if (hum >= 0 and hum < 25):
                print("very dry : %d" % hum)
            elif (hum >= 25 and hum < 50):
                print("dry : %d" % hum)
            elif (hum >= 50 and hum < 75):
                print("wet : %d" % hum)
            elif (hum >= 75 and hum <= 100):
                print("very wet : %d" % hum)
#             hum = round(senV1p2.value * Vref * 100, 1)
#             print(str(hum))
            time.sleep(1)
    except: KeyboardInterrupt
    subprocess.call('clear')
        