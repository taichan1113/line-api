import RPi.GPIO as GPIO
import time

# set GPIO mode
GPIO.setmode(GPIO.BCM)


# parameter
gpio_pump = 17


def runPump(sec, num_gpio):
    # setup GPIO
    GPIO.setup(num_gpio, GPIO.OUT)

    # logic
    GPIO.output(num_gpio, 1)
    time.sleep(sec)
    GPIO.output(num_gpio, 0)
                            
    # release GPIO
    GPIO.cleanup(num_gpio)
    return

if __name__ == "__main__":
    runPump(1, gpio_pump)
