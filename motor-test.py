import RPi.GPIO as GPIO
import time

# GPIO pins for ULN2003
IN1 = 23
IN2 = 18
IN3 = 27
IN4 = 22
pins = [IN1, IN2, IN3, IN4]

# Half-step sequence (smooth motion)
seq = [
    [1,0,0,1],
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1]
]

GPIO.setmode(GPIO.BCM)
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

steps_180 = 256   # ~180° rotation
delay = 0.01      # step delay

def move(steps, direction=1):
    for i in range(steps):
        for halfstep in range(8):
            for pin in range(4):
                # Choose forward or reverse sequence
                GPIO.output(pins[pin], seq[(halfstep if direction==1 else 7-halfstep)][pin])
            time.sleep(delay)

try:
    print("Starting continuous 180° back-and-forth movement. Press CTRL+C to stop.")
    while True:
        move(steps_180, direction=1)   # 180° forward
        time.sleep(0.5)
        move(steps_180, direction=-1)  # 180° backward
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStopping motor...")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
