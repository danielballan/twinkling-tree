import subprocess
import sys
import time

import board
import neopixel

PIXEL_COUNT = 50
ON = (255, 0, 0)
OFF = (0, 0, 0)
CAMERA_HOST = "pi2"
TARGET_DIRECTORY = "images"


def log(*message):
    print(*message, file=sys.stderr)


def main():
    process = subprocess.Popen(
        [
            "ssh",
             "-i",
             "picamera-key",
             "-t",  # unbuffered output
             f"pi@{CAMERA_HOST}",
             "twinkling-tree/venv/bin/python",
             "twinkling-tree/capture.py"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print("received", process.stdout.readline())  # Block until ready.
    try:
        pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, brightness=1, auto_write=False)
        pixels.fill(OFF)
        for i in range(PIXEL_COUNT):
            pixels[i - 1] = OFF
            pixels[i] = ON
            pixels.show()
            time.sleep(0.05)
            log(f"Requesting image {i}")
            process.stdin.write(f"{TARGET_DIRECTORY}/pixel_{i:03}.png\n".encode())
            process.stdin.flush()
            log("received from ssh", process.stdout.readline())
            log(f"Completed image {i}")
        process.stdin.close()
    finally:
        process.terminate()
        process.wait()
        pixels.fill(OFF)
        pixels.show()


if __name__ == "__main__":
    main()
