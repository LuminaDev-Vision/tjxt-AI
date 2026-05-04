import logging
from typing import Any

from openai import AsyncOpenAI

from app.clients.vector_client import vector_delete, vector_insert, vector_search
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:

    async def save(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        import uuid

        doc_id = uuid.uuid4().hex
        embedding = await self._get_embedding(text)
        await vector_insert(doc_id, text, embedding, metadata)
        return doc_id

    async def delete(self, doc_id: str):
        await vector_delete(doc_id)

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        embedding = await self._get_embedding(query)
        return await vector_search(embedding, top_k)

    async def _get_embedding(self, text: str) -> list[float]:
        client = AsyncOpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
