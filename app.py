import time, random, subprocess, threading
import RPi.GPIO as GPIO
from picamera2 import Picamera2
from ultralytics import YOLO
from flask import Flask, render_template, send_file, jsonify
import cv2, os

# ======================
# CONFIG
# ======================
PIR_PIN = 17
SOUNDS = [
    "/home/jakeagra/scarecrow/sounds/dog-bark.mp3",
    "/home/jakeagra/scarecrow/sounds/screaming-hawk.mp3",
    "/home/jakeagra/scarecrow/sounds/dog.mp3"
]
DETECTION_CLASSES = ["person","cat","dog","bird","cow","sheep","horse","mouse"]
SNAP_PATH = "/home/jakeagra/scarecrow/static/latest.jpg"
COOLDOWN = 5  # seconds

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

model = YOLO("yolov8n.pt")

# Make sure static folder exists
os.makedirs(os.path.dirname(SNAP_PATH), exist_ok=True)

app = Flask(__name__, static_folder="static")
last_detection_time = 0
# Store the latest detected animals (thread-safe for simple use)
latest_detected_animals = []
# Store status for camera and motion
status_info = {"camera_on": False, "motion": False}

def play_random_sound():
    sound = random.choice(SOUNDS)
    print(f"🔊 Playing sound: {sound}")
    subprocess.run(["mpg123", "-q", sound], check=True)

def detection_loop():
    global last_detection_time
    while True:
        motion = GPIO.input(PIR_PIN)
        status_info["motion"] = bool(motion)
        if motion:
            print("[⚠️] Motion detected!")
            time.sleep(0.2)  # debounce

            # ---- CAMERA ON ----
            print("[📸] Starting camera...")
            status_info["camera_on"] = True
            picam2 = Picamera2()
            config = picam2.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            picam2.configure(config)
            picam2.start()
            time.sleep(1)  # allow exposure to settle

            frame = picam2.capture_array()
            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(SNAP_PATH, bgr)   # Save snapshot for the web page

            # ---- YOLO DETECTION ----
            results = model(frame)
            labels = results[0].names

            detected = [labels[int(c)] for c in results[0].boxes.cls]
            print(f"[INFO] Detected: {detected}")
            global latest_detected_animals
            latest_detected_animals = detected

            if any(obj in DETECTION_CLASSES for obj in detected):
                if time.time() - last_detection_time > COOLDOWN:
                    print("[🚨] Target animal detected! Playing sound...")
                    play_random_sound()
                    last_detection_time = time.time()
            else:
                print("[INFO] No target animals found.")

            # ---- CAMERA OFF ----
            picam2.stop()
            picam2.close()
            status_info["camera_on"] = False
            print("[INFO] Camera OFF to save power.")

            time.sleep(COOLDOWN)  # small cooldown
        else:
            status_info["camera_on"] = False
        time.sleep(0.1)
# API endpoint for status
@app.route("/status")
def status():
    return jsonify(status_info)


# Main page
@app.route("/")
def index():
    # If no image yet, show placeholder
    if not os.path.exists(SNAP_PATH):
        return render_template("index.html", image_url=None)
    return render_template("index.html", image_url="/static/latest.jpg")

# API endpoint for detected animals
@app.route("/detected_animals")
def detected_animals():
    return jsonify({"animals": latest_detected_animals})

if __name__ == "__main__":
    try:
        t = threading.Thread(target=detection_loop, daemon=True)
        t.start()
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        GPIO.cleanup()
