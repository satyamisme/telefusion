from typing import Union

import telefusion
from telefusion import raw


class UnbanChatMember:
    async def unban_chat_member(
        self: "telefusion.Client",
        chat_id: Union[int, str],
        user_id: Union[int, str]
    ) -> bool:
        await self.invoke(
            raw.functions.channels.EditBanned(
                channel=await self.resolve_peer(chat_id),
                participant=await self.resolve_peer(user_id),
                banned_rights=raw.types.ChatBannedRights(
                    until_date=0
                )
            )
        )

        return True
