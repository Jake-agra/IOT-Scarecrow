import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2

# ===========================
# CONFIGURATION
# ===========================
PIR_PIN = 17                 # GPIO pin for PIR sensor
MODEL_PATH = "yolov8n.pt"   # Small YOLO model (faster). Replace with your trained model if any.
TARGET_CLASSES = ["person", "bird", "cat", "dog"]  # Objects of interest
MIN_TRIGGER_INTERVAL = 10   # Seconds between valid triggers to avoid spam

# ===========================
# SETUP
# ===========================
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))  # Lower res = faster
picam2.start()

model = YOLO(MODEL_PATH)
last_trigger_time = 0

print("✅ System ready: Waiting for PIR motion...")

try:
    while True:
        if GPIO.input(PIR_PIN):  # Motion detected by PIR
            current_time = time.time()
            if current_time - last_trigger_time > MIN_TRIGGER_INTERVAL:
                print("⚡ PIR triggered! Capturing frame...")
                frame = picam2.capture_array()

                # Run YOLO detection
                results = model(frame, verbose=False)[0]
                detected_classes = [model.names[int(c)] for c in results.boxes.cls]

                # Check if any target class is in detected list
                if any(obj in TARGET_CLASSES for obj in detected_classes):
                    print(f"🚨 ALERT! Detected: {set(detected_classes)}")
                else:
                    print(f"ℹ️ Motion detected, but no target object found ({detected_classes})")

                last_trigger_time = current_time
            else:
                print("⏳ Ignored: Too soon since last detection.")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nStopping system...")
finally:
    GPIO.cleanup()
    picam2.stop()
