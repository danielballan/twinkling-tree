import contextlib
import json
import logging
import os
import random
import re
import sys
import threading
import time
from pathlib import Path

import board
import neopixel
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


# On CircuitPlayground Express, and boards with built in status NeoPixel -> board.NEOPIXEL
# Otherwise choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D1
pixel_pin = board.D18

# On a Raspberry pi, use this instead, not all pins are supported
# pixel_pin = board.D18

# The number of NeoPixels
num_strings = 8
string_len = 50
num_pixels = string_len * num_strings

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

# Your Account SID and Auth Token from console.twilio.com
account_sid = os.environ["ACCOUNT_SID"]
auth_token  = os.environ["AUTH_TOKEN"]
phone_number = os.environ["PHONE_NUMBER"]

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER
)

def hex_to_channels(hex_code):
    """
    Convert hex code to (R, G, B) or (G, R, B) or (R, G, B, W).

    >>> hex_to_channels("#ff0000", "RGB")
    (255, 0, 0)
    """
    hex_value = hex_code.lstrip("#")
    r, g, b = tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
    return g, r, b


def dark():
    while True:
        yield (0, 0, 0)
        time.sleep(1)


def solid(color):
    while True:
        yield color
        time.sleep(1)


def string_number(number):
    "Illuminate (1-indexed) light string number"
    pixels = [(0, 0, 0)] * num_pixels
    light = [(255, 255, 255)] * string_len
    pixels[string_len * (number - 1):string_len * number] = light
    while True:
        yield pixels
        time.sleep(1)


def multicolor_random(colors):
    BATCH_SIZE = 30  # number to change in a single write
    pixels = [(0, 0, 0)] * num_pixels
    indexes = range(num_pixels)
    for index in indexes:
        pixels[index] = random.choice(colors)
    yield pixels
    while True:
        for _ in range(BATCH_SIZE):
            index = random.choice(indexes)
            candidates = colors.copy()
            if len(colors) > 1:
                candidates.remove(tuple(pixels[index]))
            pixels[index] = random.choice(candidates)
        yield pixels


def color_chase(colors, wait):
    pixels = [(0, 0, 0)] * num_pixels
    if len(colors) == 1:
        # After the initial iteration there is nothing to see,
        # as the color just overwrites itself. Add black into the mix.
        colors = [*colors, (0, 0, 0)]
    while True:
        for color in colors:
            for i in range(num_pixels):
                pixels[i] = color
                yield pixels
                time.sleep(wait)
            time.sleep(0.5)


def colorwheel(pos):
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
    return (g, r, b)



def rainbow_cycle(wait):
    pixels = [(0, 0, 0)] * num_pixels
    while True:
        for j in range(255):
            for i in range(num_pixels):
                rc_index = (i * 256 // num_pixels) + j
                pixels[i] = colorwheel(rc_index & 255)
            yield pixels
            time.sleep(wait)

levels = (0.7, 1, 1)  # GRB
gamma = 2.0
program = dark()


def correct_color(color):
    return [
        round((channel_level * channel_color) ** 1/gamma)
        for channel_level, channel_color in zip(levels, color)
    ]


shutdown = False  # used to stop draw_loop


def draw_loop():
    while not shutdown:
        try:
            program = get_program()
            step = next(program)
            if isinstance(step, tuple):
                # Solid color
                color = step
                pixels.fill(correct_color(color))
            if isinstance(step, list):
                # Array of colors
                for index, color in enumerate(step):
                    pixels[index] = correct_color(color)
            pixels.write()
        except Exception:
            logger.exception("Exception raised in draw_loop")


@contextlib.contextmanager
def run_draw_thread():
    global shutdown

    draw_thread = threading.Thread(target=draw_loop)
    draw_thread.start()
    yield
    shutdown = Ture
    draw_thread.join()


def set_program(program_):
    global program

    program = program_


def get_program():
    return program


def set_levels(levels_):
    global levels

    levels = levels_


class ParseError(ValueError):
    pass


HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
LEVELS = re.compile("levels (\d\.?\d*) (\d\.?\d*) (\d\.?\d*)")
GAMMA = re.compile("gamma (\d\.?\d*)")


# This mapping of color names -> hex values is taken from
# a survey run by Randall Munroe see:
# https://blog.xkcd.com/2010/05/03/color-survey-results/
# for more details.  The results are hosted at
# https://xkcd.com/color/rgb
# and also available as a text file at
# https://xkcd.com/color/rgb.txt
#
# License: http://creativecommons.org/publicdomain/zero/1.0/
XKCD_COLORS = json.loads((Path(__file__).parent / "colors.json").read_text())


def parse_color_token(token):
    if HEX_COLOR.match(token):
        # token is a hex color code, like '#ff0000'
        hex_color = token
    else:
        # Try parsing token as a color word (or compound word).
        hex_color = XKCD_COLORS.get(token)
        if hex_color is None:
            raise ParseError(repr(token))
    return hex_to_channels(hex_color)


def parse_color_text(text):
    "Given text like 'red' or 'red, green', return list of GRB tuples."
    tokens = (x.strip() for x in text.split(","))
    tokens = (x for x in tokens if x)
    return [*map(parse_color_token, tokens)]


def parse_text(text):
    global levels
    global gamma
    
    text = text.casefold().strip()
    if text == "dark":
        return dark()
    if text == "rainbow":
        return rainbow_cycle(0)
    if text == "princess kate":
        return multicolor_random(parse_color_text("rose, lavender"))
    if text == "april":
        return multicolor_random(parse_color_text("#f48700, #e5cf8c, #a37319"))
    if text.isnumeric():
        return string_number(int(text))
    if text.startswith("twinkle "):
        colors = parse_color_text(text[len("twinkle "):])
        return multicolor_random(colors + [(0, 0, 0)] * len(colors))
    if text.startswith("chase "):
        return color_chase(parse_color_text(text[len("chase "):]), 0)
    levels_match = LEVELS.match(text)
    if levels_match:
        levels = tuple(float(x) for x in levels_match.groups())
        return program  # no change in program
    gamma_match = GAMMA.match(text)
    if gamma_match:
        candidate_gamma = float(gamma_match.group(1))
        if candidate_gamma < 1:
            raise ParseError(f"gamma value must be >=1; got {gamma}")
        gamma = candidate_gamma
        return program  # no change in program
    # Interpret entire message as color word(s).
    tokens = parse_color_text(text)
    if len(tokens) == 1:
        return solid(tokens[0])
    else:
        return multicolor_random(tokens)


async def route(request):
    async with request.form() as form:
        text = form["Body"]
        logger.info('From %s: %r', form["From"], form["Body"])
    try:
        program = parse_text(text)
    except ParseError as err:
        logger.exception(f"Could not parse {err.args[0]}")
    else:
        logger.info("Parsed command %s", program.__name__)
        set_program(program)
    return JSONResponse({})  # TODO


class ThreadedServer(uvicorn.Server):
    # https://github.com/encode/uvicorn/discussions/1103#discussioncomment-941726

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            # Wait for server to start up, or raise TimeoutError.
            for _ in range(100):
                time.sleep(0.1)
                if self.started:
                    break
            else:
                raise TimeoutError("Server did not start in 10 seconds.")
            host, port = self.servers[0].sockets[0].getsockname()
            yield f"http://{host}:{port}"
        finally:
            self.should_exit = True
            thread.join()


app = Starlette(debug=True, routes=[
    Route('/connector/sms', route, methods=["POST"]),
])


if __name__ == "__main__":
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, loop="asyncio")
    server = ThreadedServer(config)
    with server.run_in_thread() as url:
        with run_draw_thread():
            if (len(sys.argv) > 1) and (sys.argv[1] == "--headless"):
                print('headless', file=sys.stderr)
                while True:
                    time.sleep(1)
            else:
                print('interactive', file=sys.stderr)
                while True:
                    text = input("> ")
                    try:
                        program = parse_text(text)
                    except ParseError as err:
                        logger.exception(f"Could not parse {err.args[0]}")
                    else:
                        set_program(program)


