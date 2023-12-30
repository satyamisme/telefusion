from typing import Union

import telefusion
from telefusion import raw
from telefusion import types


class AddContact:
    async def add_contact(
        self: "telefusion.Client",
        user_id: Union[int, str],
        first_name: str,
        last_name: str = "",
        phone_number: str = "",
        share_phone_number: bool = False
    ):
        r = await self.invoke(
            raw.functions.contacts.AddContact(
                id=await self.resolve_peer(user_id),
                first_name=first_name,
                last_name=last_name,
                phone=phone_number,
                add_phone_privacy_exception=share_phone_number
            )
        )

        return types.User._parse(self, r.users[0])
