import telefusion
from telefusion import raw


class UpdateProfile:
    async def update_profile(
        self: "telefusion.Client",
        first_name: str = None,
        last_name: str = None,
        bio: str = None
    ) -> bool:
        return bool(
            await self.invoke(
                raw.functions.account.UpdateProfile(
                    first_name=first_name,
                    last_name=last_name,
                    about=bio
                )
            )
        )
