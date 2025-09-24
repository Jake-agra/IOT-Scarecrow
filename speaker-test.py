import subprocess
import random
import time

SOUNDS = [
    "/home/jakeagra/scarecrow/sounds/dog-bark.mp3",
    "/home/jakeagra/scarecrow/sounds/screaming-hawk.mp3",
    "/home/jakeagra/scarecrow/sounds/dog.mp3"
]

def play_random():
    sound = random.choice(SOUNDS)
    print(f"🔊 Playing: {sound}")
    # Wait for playback to complete before returning
    subprocess.run(["mpg123", "-q", sound], check=True)

# Test: play 3 random sounds with pauses
for i in range(3):
    play_random()
    time.sleep(2)   # small gap
