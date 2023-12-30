from typing import List

import telefusion
from telefusion import raw
from telefusion import types


class GetCustomEmojiStickers:
    async def get_custom_emoji_stickers(
        self: "telefusion.Client",
        custom_emoji_ids: List[int],
    ) -> List["types.Sticker"]:
        result = await self.invoke(
            raw.functions.messages.GetCustomEmojiDocuments(
                document_id=custom_emoji_ids
            )
        )

        stickers = []
        for item in result:
            attributes = {type(i): i for i in item.attributes}
            sticker = await types.Sticker._parse(self, item, attributes)
            stickers.append(sticker)

        return telefusion.types.List(stickers)
