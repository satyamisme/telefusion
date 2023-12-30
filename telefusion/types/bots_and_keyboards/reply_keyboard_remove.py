import telefusion
from telefusion import raw
from ..object import Object


class ReplyKeyboardRemove(Object):
    def __init__(
        self,
        selective: bool = None
    ):
        super().__init__()

        self.selective = selective

    @staticmethod
    def read(b):
        return ReplyKeyboardRemove(
            selective=b.selective
        )

    async def write(self, _: "telefusion.Client"):
        return raw.types.ReplyKeyboardHide(
            selective=self.selective or None
        )
