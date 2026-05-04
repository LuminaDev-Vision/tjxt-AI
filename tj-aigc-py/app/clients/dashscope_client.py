import logging
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    return _client


async def dashscope_chat(messages: list[dict], tools: list[dict] | None = None) -> str:
    kwargs: dict = {
        "model": settings.DASHSCOPE_MODEL,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools

    response = await _get_client().chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


async def dashscope_chat_stream(
    messages: list[dict], tools: list[dict] | None = None
) -> AsyncGenerator[str, None]:
    kwargs: dict = {
        "model": settings.DASHSCOPE_MODEL,
        "messages": messages,
        "stream": True,
    }
    if tools:
        kwargs["tools"] = tools

    stream = await _get_client().chat.completions.create(**kwargs)
    async for chunk in stream:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content
