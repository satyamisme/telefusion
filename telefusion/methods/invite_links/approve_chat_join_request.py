from typing import Union

import telefusion
from telefusion import raw


class ApproveChatJoinRequest:
    async def approve_chat_join_request(
        self: "telefusion.Client",
        chat_id: Union[int, str],
        user_id: int,
    ) -> bool:
        await self.invoke(
            raw.functions.messages.HideChatJoinRequest(
                peer=await self.resolve_peer(chat_id),
                user_id=await self.resolve_peer(user_id),
                approved=True
            )
        )

        return True
