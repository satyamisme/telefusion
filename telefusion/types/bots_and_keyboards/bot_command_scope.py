import telefusion
from telefusion import raw
from ..object import Object


class BotCommandScope(Object):
    def __init__(self, type: str):
        super().__init__()

        self.type = type

    async def write(self, client: "telefusion.Client") -> "raw.base.BotCommandScope":
        raise NotImplementedError
