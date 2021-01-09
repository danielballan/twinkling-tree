import time

import board
import neopixel

PIXEL_COUNT = 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def main():
    try:
        pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, brightness=1, auto_write=False)
        while True:
            pixels.fill(WHITE)
            pixels.show()
            time.sleep(5)
            pixels.fill(BLACK)
            pixels.show()
            time.sleep(5)
    finally:
        pixels.fill(BLACK)
        pixels.show()


if __name__ == "__main__":
    main()
