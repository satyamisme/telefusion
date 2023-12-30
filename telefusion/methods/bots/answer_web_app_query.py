import telefusion
from telefusion import raw
from telefusion import types


class AnswerWebAppQuery:
    async def answer_web_app_query(
        self: "telefusion.Client",
        web_app_query_id: str,
        result: "types.InlineQueryResult"
    ) -> "types.SentWebAppMessage":
        r = await self.invoke(
            raw.functions.messages.SendWebViewResultMessage(
                bot_query_id=web_app_query_id,
                result=await result.write(self)
            )
        )

        return types.SentWebAppMessage._parse(r)
