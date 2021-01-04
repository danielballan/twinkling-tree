import asyncio
import itertools
import random

import neopixel
import toolz

from ..utils import get_pixels


RED = (255, 0, 0)
ORANGE = (100, 100, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (200, 0, 200)
CLASSIC_CHRISTMAS = [RED, ORANGE, GREEN, BLUE]


async def randomly_fill(pixels, colors):
    colors = list(colors)
    num_pixels = len(pixels)
    indexes = list(range(num_pixels))
    random.shuffle(indexes)  # in place
    partitioned = toolz.partition_all(num_pixels // len(colors), indexes)
    # Paint each partition with one color. If the pixels do not partition
    # evenly into equal sizes, paint the leftovers with the last color.
    for color, partition in itertools.zip_longest(colors, partitioned, fillvalue=colors[-1]):
        for index in partition:
            pixels[index] = color
    await pixels.ashow()
    # Block until cancelled.
    while True:
        await asyncio.sleep(10)


async def main():
    pixels = get_pixels()
    try:
        await randomly_fill(pixels, CLASSIC_CHRISTMAS)
    except KeyboardInterrupt:
        # Silently clean up and exit.
        pass
    finally:
        pixels.fill((0, 0, 0))
        await pixels.ashow()


if __name__ == "__main__":
    asyncio.run(main())
