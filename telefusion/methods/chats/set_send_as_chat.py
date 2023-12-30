from typing import Union

import telefusion
from telefusion import raw


class SetSendAsChat:
    async def set_send_as_chat(
        self: "telefusion.Client",
        chat_id: Union[int, str],
        send_as_chat_id: Union[int, str]
    ) -> bool:
        return await self.invoke(
            raw.functions.messages.SaveDefaultSendAs(
                peer=await self.resolve_peer(chat_id),
                send_as=await self.resolve_peer(send_as_chat_id)
            )
        )
