import RPi.GPIO as GPIO, time
PIR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Monitoring raw PIR pin (Ctrl-C to stop)...")
try:
    last = GPIO.input(PIR_PIN)
    while True:
        v = GPIO.input(PIR_PIN)
        if v != last:
            print(time.strftime("%Y-%m-%d %H:%M:%S"), "STATE:", v)
            last = v
        time.sleep(0.05)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
