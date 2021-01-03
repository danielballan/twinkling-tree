import asyncio

import board
import neopixel


class AsyncNeoPixel(neopixel.NeoPixel):
    async def afill(self):
        await asyncio.get_running_loop().run_in_executor(None, self.fill)

    async def ashow(self):
        await asyncio.get_running_loop().run_in_executor(None, self.show)

    async def block(self):
        ...

    # def __len__(self):
    #     return self.num


def get_pixels():

    # On CircuitPlayground Express, and boards with built in status NeoPixel -> board.NEOPIXEL
    # Otherwise choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D1
    pixel_pin = board.D18

    # On a Raspberry pi, use this instead, not all pins are supported
    # pixel_pin = board.D18

    # The number of NeoPixels
    num_pixels = 100

    # The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
    # For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
    ORDER = neopixel.GRB

    return AsyncNeoPixel(
        pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER
    )
