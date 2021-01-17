import asyncio

from ..utils import get_pixels


L = 50  # lights per string


async def string_number(pixels, n):
    pixels.fill((0, 0, 0))
    for rel_index in range(0, L):
        index = n * L + rel_index
        pixels[index] = (255, 255, 255)
    await pixels.ashow()


async def main():
    pixels = get_pixels()
    num_strings = len(pixels) // L
    try:
        while True:
            for n in range(num_strings):
                await string_number(pixels, n)
                await asyncio.sleep(10)
    except KeyboardInterrupt:
        # Silently clean up and exit.
        pass
    finally:
        pixels.fill((0, 0, 0))
        await pixels.ashow()


if __name__ == "__main__":
    asyncio.run(main())
