import subprocess
import sys
import time

import board
import neopixel

PIXEL_COUNT = 50
ON = (255, 0, 0)
OFF = (0, 0, 0)
CAMERA_HOST = "pi2"


def log(message):
    print(message, file=sys.stderr)


def main():
    process = subprocess.Popen(["ssh", "pi2", "python", "twinkling-tree/capture.py"])
    process.stdout.readline()  # Block until ready.
    try:
        pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, brightness=1, auto_write=False)
        pixels.fill(OFF)
            for i in range(PIXEL_COUNT):
                pixels[i - 1] = OFF 
                pixels[i] = ON
                pixels.show()
                time.sleep(0.05)
                log(f"Requesting image {i}")
                process.stdin(f"light-{i}.png")
                process.stdout.readline()
                log(f"Completed image {i}")
        process.stdin.close()
    finally:
        pixels.fill(OFF)
        pixels.show()


if __name__ == "__main__":
    main()
