import asyncio
import random

from ..utils import get_pixels


RED = (255, 0, 0)
ORANGE = (100, 100, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (200, 0, 200)
CLASSIC_CHRISTMAS = [RED, ORANGE, GREEN, BLUE]
BATCH_SIZE = 10  # number to change in a single write


async def randomly_fill(pixels, colors):
    colors = list(colors)
    num_pixels = len(pixels)
    indexes = list(range(num_pixels))
    for index in indexes:
        pixels[index] = random.choice(colors)
    await pixels.ashow()
    while True:
        for _ in range(BATCH_SIZE):
            index = random.choice(indexes)
            candidates = colors.copy()
            if len(colors) > 1:
                candidates.remove(tuple(pixels[index]))
            pixels[index] = random.choice(candidates)
        await pixels.ashow()


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
