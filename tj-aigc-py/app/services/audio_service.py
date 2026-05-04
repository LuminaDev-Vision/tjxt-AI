import logging
from collections.abc import AsyncGenerator

from app.clients.openai_client import openai_stt, openai_tts_stream

logger = logging.getLogger(__name__)


class AudioService:

    async def tts_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        async for chunk in openai_tts_stream(text):
            yield chunk

    async def stt(self, audio_data: bytes) -> str:
        text = await openai_stt(audio_data)
        try:
            from opencc import OpenCC

            cc = OpenCC("t2s")
            return cc.convert(text)
        except Exception:
            return text
