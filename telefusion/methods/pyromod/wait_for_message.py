import asyncio
import telefusion
from typing import Union
from functools import partial

from telefusion import types
from telefusion.filters import Filter

class WaitForMessage:
    async def wait_for_message(
        self: "telefusion.Client",
        chat_id: Union[int, str],
        filters: Filter = None,
        timeout: int = None
    ) -> "types.Message":
        if not isinstance(chat_id, int):
            chat = await self.get_chat(chat_id)
            chat_id = chat.id

        conversation_handler = self.dispatcher.conversation_handler
        future = self.loop.create_future()
        future.add_done_callback(
            partial(
                conversation_handler.delete_waiter,
                chat_id
            )
        )
        waiter = dict(future=future, filters=filters, update_type=types.Message)
        conversation_handler.waiters[chat_id] = waiter
        return await asyncio.wait_for(future, timeout=timeout)