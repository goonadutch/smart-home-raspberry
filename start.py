from hcrs import HCRS
from led import LED
from buzzer import Buzzer
import RPi.GPIO as GPIO
import time
import _thread
import requests

# setup
GPIO.setmode(GPIO.BOARD)

BUZZER = 12
TRIG = 16
ECHO = 18
WARNINGLED = 38
DANGERLED = 40

GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.IN)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)

# initialize components
sensor = HCRS(TRIG, ECHO, 2)
warningLed = LED(WARNINGLED)
dangerLed = LED(DANGERLED)
buzz = Buzzer(BUZZER, 1)

def send_data(distance):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
        url = "https://home-security.adaptable.app/update/" + str(distance)
        r = requests.get(url, headers=headers)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
    except Exception as e:
        print(e)

def print_and_send_stuff(distance):
    print ("Distance:", distance, "cm")
    send_data(distance)

# start all
def buzzing(buzz):
    while True:
        if buzz.status == "ON":
            buzz.blink()
        else:
            buzz.stop()
        

try:
    _thread.start_new_thread(buzzing, (buzz, ))
    while True:
        distance = sensor.read()
        if distance == -1:
            print ("Distance Is Out Of Range")
            warningLed.off()
            dangerLed.off()
        else:
            if distance <= 22:
                buzz.status = "ON"
                buzz.setDelay(float(distance * 0.1))
                warningLed.on()
                dangerLed.off()
                if distance < 12:
                    buzz.setDelay(float(distance * 0.03))
                    warningLed.off()    
                    dangerLed.on()
            else:
                buzz.status = "OFF"
                warningLed.off()
                dangerLed.off()
            print_and_send_stuff(distance)
            # await send_data(distance)

except Exception:
    buzz.stop()
    warningLed.off()
    dangerLed.off()
    GPIO.cleanup()
except KeyboardInterrupt:
    buzz.stop()
    warningLed.off()    
    dangerLed.off()
    GPIO.cleanup()
