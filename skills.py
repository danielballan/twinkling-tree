import asyncio

from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

from twinkling_tree.stunts.rainbow import infinite_rainbow_cycle
from twinkling_tree.utils import get_pixels


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

    @match_regex(r'rainbow', case_sensitive=False)
    async def rainbow(self, message):
        await self._controller.schedule(infinite_rainbow_cycle(self._pixels, 0.001))
        await message.respond('OK, making a \N{RAINBOW}')

    @match_regex(r'dark', case_sensitive=False)
    async def dark(self, message):
        await message.respond('OK, going dark')
        await self._controller.schedule(dark(self._pixels))
