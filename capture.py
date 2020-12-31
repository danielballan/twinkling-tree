import sys
import time

import picamera


def log(message):
    print(message, file=sys.stderr)


def setup(camera):
    """
    Fix settings so that image sequence has consistent gain etc.
    """
    log("Setup started")
    camera.resolution = (1280, 720)
    camera.framerate = 30
    # Wait for the automatic gain control to settle
    time.sleep(2)
    # Now fix the values
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    log("Setup complete")


def capture_loop(camera, filepaths):
    """
    Consume an iterable of filepaths, capturing an image for each.
    """
    log("Capture loop started. Enter filepaths one line at a time. Use Ctrl+D to finish.")
    for filepath in filepaths:
        print('filepath', repr(filepath), type(filepath))
        camera.capture(filepath)
        log(f"Captured {filepath}")


def main():
    """
    Read filepaths from the stdin and save an image for each.
    """
    with picamera.PiCamera() as camera:
        setup(camera)
        filepaths = (line.rstrip("\n") for line in sys.stdin)
        capture_loop(camera, filepaths)
    log("Received EOF. Exiting.")


if __name__ == "__main__":
    main()
