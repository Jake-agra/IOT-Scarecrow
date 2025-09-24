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
DETECTION_CLASSES = ["cat", "dog", "bird", "cow", "sheep", "horse"]
COOLDOWN = 3   # seconds after each detection cycle

# ==============================
# INITIALIZE HARDWARE
# ==============================
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Load YOLO model once to save time
model = YOLO("yolov8n.pt")  # lightweight model for Raspberry Pi

def play_random_sound():
    sound = random.choice(SOUNDS)
    print(f"🔊 Playing sound: {sound}")
    subprocess.run(["mpg123", "-q", sound], check=True)

print("[INFO] System armed. Waiting for motion...")

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("[⚠️] Motion detected! Turning on camera...")
            time.sleep(0.2)  # small debounce

            # ---- CAMERA START ----
            picam2 = Picamera2()
            config = picam2.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            picam2.configure(config)
            picam2.start()
            time.sleep(1)  # allow auto-exposure to settle

            print("[📸] Camera active. Displaying live view...")
            frame = None

            # Small live-preview loop (1–2 seconds)
            start_time = time.time()
            while time.time() - start_time < 5:      # show for ~2 seconds
                frame = picam2.capture_array()
                bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.imshow("Scarecrow Live", bgr)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise KeyboardInterrupt

            # ---- YOLO DETECTION ----
            print("[🔎] Running YOLO detection...")
            results = model(frame)
            labels = results[0].names
            detected = [labels[int(c)] for c in results[0].boxes.cls]
            print(f"[INFO] Detected: {detected}")

            # Check for target animals
            if any(obj in DETECTION_CLASSES for obj in detected):
                print("[🚨] Animal detected! Triggering scare sound...")
                play_random_sound()
            else:
                print("[INFO] No target animals found.")

            # ---- STOP CAMERA ----
            picam2.stop()
            picam2.close()
            cv2.destroyAllWindows()
            print("[INFO] Camera turned OFF to save power.")

            # ---- COOLDOWN ----
            print(f"[INFO] Cooling down for {COOLDOWN}s...")
            time.sleep(COOLDOWN)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[INFO] Shutting down...")
finally:
    GPIO.cleanup()
    cv2.destroyAllWindows()
