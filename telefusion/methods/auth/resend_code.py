import logging

import telefusion
from telefusion import raw
from telefusion import types

log = logging.getLogger(__name__)


class ResendCode:
    async def resend_code(
        self: "telefusion.Client",
        phone_number: str,
        phone_code_hash: str
    ) -> "types.SentCode":
        phone_number = phone_number.strip(" +")

        r = await self.invoke(
            raw.functions.auth.ResendCode(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash
            )
        )

        return types.SentCode._parse(r)
