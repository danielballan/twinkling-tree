import asyncio

from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

from twinkling_tree.stunts.rainbow import infinite_rainbow_cycle
from twinkling_tree.stunts.color import randomly_fill
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

    @match_regex(r"rainbow", case_sensitive=False)
    async def rainbow(self, message):
        await self._controller.schedule(infinite_rainbow_cycle(self._pixels, 0.001))
        await message.respond("OK, making a \N{RAINBOW}")

    @match_regex(r"dark", case_sensitive=False)
    async def dark(self, message):
        await message.respond("OK, going dark")
        await self._controller.schedule(dark(self._pixels))

    @match_regex(r'color (?P<color_terms>.*)', case_sensitive=False)
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
        for color_term in color_terms:
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
        await message.respond('OK, coloring')
        await self._controller.schedule(randomly_fill(self._pixels, colors))
