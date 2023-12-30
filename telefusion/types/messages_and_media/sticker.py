from datetime import datetime
from typing import List, Dict, Type

import telefusion
from telefusion import raw, utils
from telefusion import types
from telefusion.errors import StickersetInvalid
from telefusion.file_id import FileId, FileType, FileUniqueId, FileUniqueType
from ..object import Object


class Sticker(Object):
    def __init__(
        self,
        *,
        client: "telefusion.Client" = None,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        is_animated: bool,
        is_video: bool,
        file_name: str = None,
        mime_type: str = None,
        file_size: int = None,
        date: datetime = None,
        emoji: str = None,
        set_name: str = None,
        thumbs: List["types.Thumbnail"] = None
    ):
        super().__init__(client)

        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size
        self.date = date
        self.width = width
        self.height = height
        self.is_animated = is_animated
        self.is_video = is_video
        self.emoji = emoji
        self.set_name = set_name
        self.thumbs = thumbs

    cache = {}

    @staticmethod
    async def _get_sticker_set_name(invoke, input_sticker_set_id):
        try:
            set_id = input_sticker_set_id[0]
            set_access_hash = input_sticker_set_id[1]

            name = Sticker.cache.get((set_id, set_access_hash), None)

            if name is not None:
                return name

            name = (await invoke(
                raw.functions.messages.GetStickerSet(
                    stickerset=raw.types.InputStickerSetID(
                        id=set_id,
                        access_hash=set_access_hash
                    ),
                    hash=0
                )
            )).set.short_name

            Sticker.cache[(set_id, set_access_hash)] = name

            if len(Sticker.cache) > 250:
                for i in range(50):
                    Sticker.cache.pop(next(iter(Sticker.cache)))

            return name
        except StickersetInvalid:
            return None

    @staticmethod
    async def _parse(
        client,
        sticker: "raw.types.Document",
        document_attributes: Dict[Type["raw.base.DocumentAttribute"], "raw.base.DocumentAttribute"],
    ) -> "Sticker":
        sticker_attributes = (
            document_attributes[raw.types.DocumentAttributeSticker]
            if raw.types.DocumentAttributeSticker in document_attributes
            else document_attributes[raw.types.DocumentAttributeCustomEmoji]
        )

        image_size_attributes = document_attributes.get(raw.types.DocumentAttributeImageSize, None)
        file_name = getattr(document_attributes.get(raw.types.DocumentAttributeFilename, None), "file_name", None)
        video_attributes = document_attributes.get(raw.types.DocumentAttributeVideo, None)

        sticker_set = sticker_attributes.stickerset

        if isinstance(sticker_set, raw.types.InputStickerSetID):
            input_sticker_set_id = (sticker_set.id, sticker_set.access_hash)
            set_name = await Sticker._get_sticker_set_name(client.invoke, input_sticker_set_id)
        else:
            set_name = None

        return Sticker(
            file_id=FileId(
                file_type=FileType.STICKER,
                dc_id=sticker.dc_id,
                media_id=sticker.id,
                access_hash=sticker.access_hash,
                file_reference=sticker.file_reference
            ).encode(),
            file_unique_id=FileUniqueId(
                file_unique_type=FileUniqueType.DOCUMENT,
                media_id=sticker.id
            ).encode(),
            width=(
                image_size_attributes.w
                if image_size_attributes
                else video_attributes.w
                if video_attributes
                else 512
            ),
            height=(
                image_size_attributes.h
                if image_size_attributes
                else video_attributes.h
                if video_attributes
                else 512
            ),
            is_animated=sticker.mime_type == "application/x-tgsticker",
            is_video=sticker.mime_type == "video/webm",
            set_name=set_name,
            emoji=sticker_attributes.alt or None,
            file_size=sticker.size,
            mime_type=sticker.mime_type,
            file_name=file_name,
            date=utils.timestamp_to_datetime(sticker.date),
            thumbs=types.Thumbnail._parse(client, sticker),
            client=client
        )
