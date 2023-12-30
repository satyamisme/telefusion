import html
import logging
import re
from html.parser import HTMLParser
from typing import Optional

import telefusion
from telefusion import raw
from telefusion.enums import MessageEntityType
from telefusion.errors import PeerIdInvalid
from . import utils

log = logging.getLogger(__name__)


class Parser(HTMLParser):
    MENTION_RE = re.compile(r"tg://user\?id=(\d+)")

    def __init__(self, client: "telefusion.Client"):
        super().__init__()

        self.client = client

        self.text = ""
        self.entities = []
        self.tag_entities = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        extra = {}

        if tag in ["b", "strong"]:
            entity = raw.types.MessageEntityBold
        elif tag in ["i", "em"]:
            entity = raw.types.MessageEntityItalic
        elif tag == "u":
            entity = raw.types.MessageEntityUnderline
        elif tag in ["s", "del", "strike"]:
            entity = raw.types.MessageEntityStrike
        elif tag == "blockquote":
            entity = raw.types.MessageEntityBlockquote
        elif tag == "code":
            entity = raw.types.MessageEntityCode
        elif tag == "pre":
            entity = raw.types.MessageEntityPre
            extra["language"] = attrs.get("language", "")
        elif tag == "spoiler":
            entity = raw.types.MessageEntitySpoiler
        elif tag == "a":
            url = attrs.get("href", "")

            mention = Parser.MENTION_RE.match(url)

            if mention:
                entity = raw.types.InputMessageEntityMentionName
                extra["user_id"] = int(mention.group(1))
            else:
                entity = raw.types.MessageEntityTextUrl
                extra["url"] = url
        elif tag == "emoji":
            entity = raw.types.MessageEntityCustomEmoji
            custom_emoji_id = int(attrs.get("id"))
            extra["document_id"] = custom_emoji_id
        else:
            return

        if tag not in self.tag_entities:
            self.tag_entities[tag] = []

        self.tag_entities[tag].append(entity(offset=len(self.text), length=0, **extra))

    def handle_data(self, data):
        data = html.unescape(data)

        for entities in self.tag_entities.values():
            for entity in entities:
                entity.length += len(data)

        self.text += data

    def handle_endtag(self, tag):
        try:
            self.entities.append(self.tag_entities[tag].pop())
        except (KeyError, IndexError):
            line, offset = self.getpos()
            offset += 1

            log.debug("Unmatched closing tag </%s> at line %s:%s", tag, line, offset)
        else:
            if not self.tag_entities[tag]:
                self.tag_entities.pop(tag)

    def error(self, message):
        pass


class HTML:
    def __init__(self, client: Optional["telefusion.Client"]):
        self.client = client

    async def parse(self, text: str):
        text = re.sub(r"^\s*(<[\w<>=\s\"]*>)\s*", r"\1", text)
        text = re.sub(r"\s*(</[\w</>]*>)\s*$", r"\1", text)

        parser = Parser(self.client)
        parser.feed(utils.add_surrogates(text))
        parser.close()

        if parser.tag_entities:
            unclosed_tags = []

            for tag, entities in parser.tag_entities.items():
                unclosed_tags.append(f"<{tag}> (x{len(entities)})")

            log.info("Unclosed tags: %s", ", ".join(unclosed_tags))

        entities = []

        for entity in parser.entities:
            if isinstance(entity, raw.types.InputMessageEntityMentionName):
                try:
                    if self.client is not None:
                        entity.user_id = await self.client.resolve_peer(entity.user_id)
                except PeerIdInvalid:
                    continue

            entities.append(entity)

        entities = list(filter(lambda x: x.length > 0, entities))

        return {
            "message": utils.remove_surrogates(parser.text),
            "entities": sorted(entities, key=lambda e: e.offset) or None
        }

    @staticmethod
    def unparse(text: str, entities: list):
        def parse_one(entity):
            entity_type = entity.type
            start = entity.offset
            end = start + entity.length

            if entity_type in (
                MessageEntityType.BOLD,
                MessageEntityType.ITALIC,
                MessageEntityType.UNDERLINE,
                MessageEntityType.STRIKETHROUGH,
            ):
                name = entity_type.name[0].lower()
                start_tag = f"<{name}>"
                end_tag = f"</{name}>"
            elif entity_type == MessageEntityType.PRE:
                name = entity_type.name.lower()
                language = getattr(entity, "language", "") or ""
                start_tag = f'<{name} language="{language}">' if language else f"<{name}>"
                end_tag = f"</{name}>"
            elif entity_type in (
                MessageEntityType.CODE,
                MessageEntityType.BLOCKQUOTE,
                MessageEntityType.SPOILER,
            ):
                name = entity_type.name.lower()
                start_tag = f"<{name}>"
                end_tag = f"</{name}>"
            elif entity_type == MessageEntityType.TEXT_LINK:
                url = entity.url
                start_tag = f'<a href="{url}">'
                end_tag = "</a>"
            elif entity_type == MessageEntityType.TEXT_MENTION:
                user = entity.user
                start_tag = f'<a href="tg://user?id={user.id}">'
                end_tag = "</a>"
            elif entity_type == MessageEntityType.CUSTOM_EMOJI:
                custom_emoji_id = entity.custom_emoji_id
                start_tag = f'<emoji id="{custom_emoji_id}">'
                end_tag = "</emoji>"
            else:
                return

            return (start_tag, start), (end_tag, end)

        def recursive(entity_i: int) -> int:
            this = parse_one(entities[entity_i])
            if this is None:
                return 1
            (start_tag, start), (end_tag, end) = this
            entities_offsets.append((start_tag, start))
            internal_i = entity_i + 1
            while internal_i < len(entities) and entities[internal_i].offset < end:
                internal_i += recursive(internal_i)
            entities_offsets.append((end_tag, end))
            return internal_i - entity_i

        text = utils.add_surrogates(text)

        entities_offsets = []

        entities.sort(key=lambda e: (e.offset, -e.length))

        i = 0
        while i < len(entities):
            i += recursive(i)

        if entities_offsets:
            last_offset = entities_offsets[-1][1]
            for entity, offset in reversed(entities_offsets):
                text = text[:offset] + entity + html.escape(text[offset:last_offset]) + text[last_offset:]
                last_offset = offset

        return utils.remove_surrogates(text)
