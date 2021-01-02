import asyncio
import neopixel


class AsyncNeoPixel(neopixel.NeoPixel):
    async def ashow(self):
        await asyncio.get_running_loop().run_in_executor(None, self.show)

    async def block(self):
        ...
