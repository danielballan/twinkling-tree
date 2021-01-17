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
    num_pixels = 500

    # The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
    # For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
    ORDER = neopixel.GRB

    return AsyncNeoPixel(
        pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER
    )


def hex_to_channels(hex_code, order):
    """
    Convert hex code to (R, G, B) or (G, R, B) or (R, G, B, W).

    >>> hex_to_channels("#ff0000", "RGB")
    (255, 0, 0)
    """
    hex_value = hex_code.lstrip("#")
    r, g, b = tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
    if order == neopixel.RGB:
        return r, g, b
    elif order == neopixel.GRB:
        return g, r, b
    elif order == neopixel.RGBW:
        return r, g, b, 0
    else:
        raise ValueError("order is {order}; expected 'RGB' or 'GRB' or 'RGBW'")
