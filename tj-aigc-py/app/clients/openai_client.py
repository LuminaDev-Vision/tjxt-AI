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
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
    return _client


async def openai_chat_text(messages: list[dict]) -> str:
    response = await _get_client().chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content or ""


async def openai_tts_stream(text: str) -> AsyncGenerator[bytes, None]:
    response = await _get_client().audio.speech.create(
        model=settings.OPENAI_TTS_MODEL,
        voice="alloy",
        input=text,
        response_format="mp3",
    )
    async for chunk in response.iter_bytes():
        yield chunk


async def openai_stt(audio_data: bytes) -> str:
    import io

    audio_file = io.BytesIO(audio_data)
    audio_file.name = "audio.mp3"

    response = await _get_client().audio.transcriptions.create(
        model=settings.OPENAI_STT_MODEL,
        file=audio_file,
    )
    return response.text
