import asyncio

import neopixel

from ..utils import get_pixels


def wheel(pos, byteorder):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if byteorder in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


async def rainbow_cycle(pixels, wait):
    num_pixels = len(pixels)
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255, pixels.byteorder)
        await pixels.ashow()
        await asyncio.sleep(wait)


async def infinite_rainbow_cycle(pixels, wait):
    while True:
        await rainbow_cycle(pixels, wait)


async def main():
    pixels = get_pixels()
    try:
        await infinite_rainbow_cycle(pixels, 0.001)  # rainbow cycle with 1ms delay per step
    except KeyboardInterrupt:
        # Silently clean up and exit.
        pass
    finally:
        pixels.fill((0, 0, 0))
        await pixels.ashow()


if __name__ == "__main__":
    asyncio.run(main())
