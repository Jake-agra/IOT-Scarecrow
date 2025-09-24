import time
import random
import subprocess
import RPi.GPIO as GPIO
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2

# ==============================
# CONFIGURATION
# ==============================
PIR_PIN = 17
SOUNDS = [
    "/home/jakeagra/scarecrow/sounds/dog-bark.mp3",
    "/home/jakeagra/scarecrow/sounds/screaming-hawk.mp3",
    "/home/jakeagra/scarecrow/sounds/dog.mp3"
]
DETECTION_CLASSES = ["cat", "dog", "bird", "cow", "sheep", "horse"]  # adjust to your needs

# ==============================
# INITIALIZE HARDWARE
# ==============================
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()

model = YOLO("yolov8n.pt")  # lightweight YOLO model

print("[INFO] System armed. Waiting for motion...")

def play_random_sound():
    sound = random.choice(SOUNDS)
    print(f"🔊 Playing sound: {sound}")
    subprocess.run(["mpg123", "-q", sound], check=True)

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("[⚠️] Motion detected! Capturing frame...")
            time.sleep(0.2)  # small debounce

            # Capture image (RGB)
            frame = picam2.capture_array()

            # YOLO expects BGR for cv2.imshow (but works with RGB too)
            # If you later display, convert with cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            results = model(frame)
            labels = results[0].names
            detected = [labels[int(c)] for c in results[0].boxes.cls]

            print(f"[INFO] Detected: {detected}")

            # Check if any target animals are detected
            if any(obj in DETECTION_CLASSES for obj in detected):
                print("[🚨] Animal detected! Triggering scare sound...")
                play_random_sound()
            else:
                print("[INFO] No target animals found.")

            # Avoid re-triggering too fast
            time.sleep(3)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[INFO] Shutting down...")
finally:
    GPIO.cleanup()
    picam2.stop()
