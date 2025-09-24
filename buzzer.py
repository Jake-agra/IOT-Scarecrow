import RPi.GPIO as GPIO
import time

BUZZER_PIN = 27   # Change if you used a different GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

try:
    print("🔊 Buzzer test starting...")

    for i in range(5):  # Beep 5 times
        print(f"Beep {i+1}")
        GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn buzzer ON
        time.sleep(0.5)
        GPIO.output(BUZZER_PIN, GPIO.LOW)   # Turn buzzer OFF
        time.sleep(0.5)

    print("✅ Test finished!")

except KeyboardInterrupt:
    print("\nTest interrupted by user.")

finally:
    GPIO.output(BUZZER_PIN, GPIO.LOW)  # Ensure buzzer is off
    GPIO.cleanup()
    print("GPIO cleaned up.")
