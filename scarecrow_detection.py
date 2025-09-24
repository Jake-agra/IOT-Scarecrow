from picamera2 import Picamera2
from ultralytics import YOLO
import cv2, time

model = YOLO("yolov8n.pt")
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
print("[INFO] Starting Scarecrow Detection. Press 'q' to quit...")
time.sleep(2)

while True:
    frame = picam2.capture_array()
    if frame.shape[2] == 4:                           # ✅ convert 4→3 channels
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    results = model(frame)
    annotated = results[0].plot()
    cv2.imshow("Scarecrow Detection", annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
print("[INFO] Detection stopped.")
