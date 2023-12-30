import logging
from typing import Union

import telefusion
from telefusion import raw
from telefusion import types

log = logging.getLogger(__name__)

class ExportStoryLink:
    async def export_story_link(
        self: "telefusion.Client",
        chat_id: Union[int, str],
        story_id: int,
    ) -> types.ExportedStoryLink:
        peer = await self.resolve_peer(chat_id)

        rpc = raw.functions.stories.ExportStoryLink(peer=peer, id=story_id)

        r = await self.invoke(rpc, sleep_threshold=-1)

        return types.ExportedStoryLink._parse(r)
