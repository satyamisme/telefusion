from typing import Union

import telefusion
from telefusion import raw
from .bot_command_scope import BotCommandScope


class BotCommandScopeChatAdministrators(BotCommandScope):
    def __init__(self, chat_id: Union[int, str]):
        super().__init__("chat_administrators")

        self.chat_id = chat_id

    async def write(self, client: "telefusion.Client") -> "raw.base.BotCommandScope":
        return raw.types.BotCommandScopePeerAdmins(
            peer=await client.resolve_peer(self.chat_id)
        )
