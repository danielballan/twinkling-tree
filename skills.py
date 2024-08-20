import asyncio
import subprocess

from opsdroid.constraints import constrain_users
from opsdroid.matchers import match_crontab, match_regex
from opsdroid.skill import Skill
from opsdroid.events import Message

from twinkling_tree.stunts.rainbow import infinite_rainbow_cycle
from twinkling_tree.stunts.color import randomly_fill
from twinkling_tree.stunts.string_number import string_number
from twinkling_tree.utils import hex_to_channels, get_pixels
from twinkling_tree.color_data import XKCD_COLORS


async def dark(pixels):
    pixels.fill((0, 0, 0))
    await pixels.ashow()


class Controller:
    def __init__(self):
        self.task = None

    async def schedule(self, coro):
        "Cancel the current stunt, if any, and run the new one."
        if self.task is not None:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.task = asyncio.create_task(coro)


class Rainbow(Skill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._controller = Controller()
        self._pixels = get_pixels()

    def _channels_from_name(self, color_name):
        return hex_to_channels(XKCD_COLORS[f"xkcd:{color_name}"], self._pixels.byteorder)

    @match_regex(r"rainbow", case_sensitive=False)
    async def rainbow(self, message):
        await self._controller.schedule(infinite_rainbow_cycle(self._pixels, 0.001))
        await message.respond("OK, making a \N{RAINBOW}")

    @match_regex(r"dark", case_sensitive=False)
    async def dark(self, message):
        await message.respond("OK, going dark")
        await self._controller.schedule(dark(self._pixels))

    @match_regex(r"jedi", case_sensitive=False)
    async def jedi(self, message):
        await message.respond("This is the way.")
        colors = [self._channels_from_name("electric blue")]
        await self._controller.schedule(randomly_fill(self._pixels, colors))

    @match_regex(r"sith", case_sensitive=False)
    async def sith(self, message):
        await message.respond("Come to the dark side.")
        colors = [self._channels_from_name("blood red")]
        await self._controller.schedule(randomly_fill(self._pixels, colors))

    @match_regex(r"classic", case_sensitive=False)
    async def classic(self, message):
        await message.respond("OK, here's a classic Christmas tree.")
        CLASSIC_COLORS = [
            (255, 0, 0),
            (100, 100, 0),
            (0, 255, 0),
            (0, 0, 255),
            (200, 0, 200),
        ]
        await self._controller.schedule(randomly_fill(self._pixels, CLASSIC_COLORS))

    @match_regex(r"christmas", case_sensitive=False)
    async def christmas(self, message):
        await message.respond("\N{Christmas Tree}")
        colors = [self._channels_from_name(name) for name in ("blood red", "pine green", "ivory")]
        await self._controller.schedule(randomly_fill(self._pixels, colors))

    async def color(self, message):
        order = self._pixels.byteorder
        color_terms_raw = message.entities["color_terms"]["value"].lower().strip()
        try:
            # First try to interpet this as one (possibly compound-word) valid term.
            XKCD_COLORS[f"xkcd:{color_terms_raw}"]
            color_terms = [color_terms_raw]
        except KeyError:
            # Interpret this multiple as comma- or space- separated terms.
            # Accept comma-separated terms to support compound words like sea
            # green and light blue. Also accept space-separated for usability.
            if "," in color_terms_raw:
                color_terms = [term.strip() for term in color_terms_raw.split(",")]
            else:
                color_terms = color_terms_raw.split()
        colors = []
        twinkle = 0
        for color_term in color_terms:
            if color_term == "twinkle":
                twinkle += 1
                continue
            try:
                if color_term.startswith("#"):
                    # Interpret the color term as a hex code.
                    channels = hex_to_channels(color_term, order)
                else:
                    # Interpret it as a color name and look up the hex code.
                    hex_code = XKCD_COLORS[f"xkcd:{color_term}"]
                    channels = hex_to_channels(hex_code, order)
            except KeyError:
                await message.respond(
                    f"I do not know the color {color_term}. Try something else if you like.")
                return
            colors.append(channels)
        # For each occurrence of 'twinkle', make half the lights dark
        # at any given time.
        colors += ([hex_to_channels("#000000", order)] * len(colors) * twinkle)
        await message.respond('OK, coloring')
        await self._controller.schedule(randomly_fill(self._pixels, colors))

    @match_regex(r'string (?P<num>\d+)', case_sensitive=False)
    async def string_number(self, message):
        n = int(message.entities["num"]["value"])
        await self._controller.schedule(string_number(self._pixels, n))
        await message.respond(f"Illuminating String {n}")

    @match_regex(r'reboot', case_sensitive=False)
    @constrain_users(['danielballan'])
    async def reboot(self, message):
        subprocess.Popen("Will go dark and reboot in 30 seconds.")
        await self._controller.schedule(dark(self._pixels))
        await asyncio.sleep(30)
        await message.respond("Going dark and rebooting.")
        # subprocess.Popen(["reboot", "now"])

    @match_regex(r'shutdown', case_sensitive=False)
    @constrain_users(['danielballan'])
    async def shutdown(self, message):
        subprocess.Popen("Will go dark and shut down in 30 seconds.")
        await self._controller.schedule(dark(self._pixels))
        await asyncio.sleep(30)
        await message.respond("Going dark and shutting down. Power-cycle to reboot.")
        # subprocess.Popen(["shutdown", "now"])

    @match_crontab('30 22 * * *', timezone="America/New York")
    async def timed_goodnight(self, event):
        await self._controller.schedule(dark(self._pixels))

    match_regex(r'(?P<color_terms>.*)', case_sensitive=False, score_factor=0.1)(color)
