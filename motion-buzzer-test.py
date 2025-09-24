import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2

# ===========================
# CONFIGURATION
# ===========================
PIR_PIN = 17               # PIR sensor stays on GPIO 17
BUZZER_PIN = 27            # Buzzer moved to GPIO 27
MODEL_PATH = "yolov8n.pt"  # YOLO nano model
TARGET_CLASSES = ["person", "bird", "cat", "dog"]
MIN_TRIGGER_INTERVAL = 10  # seconds between valid triggers

# ===========================
# SETUP
# ===========================
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
picam2.start()

model = YOLO(MODEL_PATH)
last_trigger_time = 0

print("✅ System ready: Waiting for PIR motion...")

try:
    while True:
        if GPIO.input(PIR_PIN):  # Motion detected
            current_time = time.time()
            if current_time - last_trigger_time > MIN_TRIGGER_INTERVAL:
                print("⚡ PIR triggered! Capturing frame...")
                frame = picam2.capture_array()

                results = model(frame, verbose=False)[0]
                detected_classes = [model.names[int(c)] for c in results.boxes.cls]

                if any(obj in TARGET_CLASSES for obj in detected_classes):
                    print(f"🚨 ALERT! Detected: {set(detected_classes)}")

                    # Buzzer ON
                    GPIO.output(BUZZER_PIN, GPIO.HIGH)
                    time.sleep(2)  # Buzzer duration
                    GPIO.output(BUZZER_PIN, GPIO.LOW)

                else:
                    print(f"ℹ️ Motion detected but no target object found ({detected_classes})")

                last_trigger_time = current_time
            else:
                print("⏳ Ignored: Too soon since last detection.")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nStopping system...")
finally:
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.cleanup()
    picam2.stop()
