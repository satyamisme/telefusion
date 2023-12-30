import telefusion


class Stop:
    async def stop(
        self: "telefusion.Client",
        block: bool = True
    ):
        async def do_it():
            await self.terminate()
            await self.disconnect()

        if block:
            await do_it()
        else:
            self.loop.create_task(do_it())

        return self
