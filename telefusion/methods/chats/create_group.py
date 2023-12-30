from typing import Union, List

import telefusion
from telefusion import raw
from telefusion import types


class CreateGroup:
    async def create_group(
        self: "telefusion.Client",
        title: str,
        users: Union[Union[int, str], List[Union[int, str]]]
    ) -> "types.Chat":
        if not isinstance(users, list):
            users = [users]

        r = await self.invoke(
            raw.functions.messages.CreateChat(
                title=title,
                users=[await self.resolve_peer(u) for u in users]
            )
        )

        return types.Chat._parse_chat(self, r.chats[0])
