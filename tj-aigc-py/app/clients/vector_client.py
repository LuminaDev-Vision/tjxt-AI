import logging
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, Text, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings

logger = logging.getLogger(__name__)

_vector_engine = None
_vector_session_factory = None


class VectorDocument(SQLModel, table=True):
    __tablename__ = "vector_documents"

    id: str = Column(String(64), primary_key=True)
    text: str = Column(Text, nullable=False)
    vector: list[float] = Column(Vector(1536), nullable=False)
    metadata_: str | None = Column("metadata", Text, nullable=True)


def _get_engine():
    global _vector_engine
    if _vector_engine is None:
        _vector_engine = create_async_engine(
            settings.PGVECTOR_URL,
            echo=settings.DEBUG,
            pool_size=5,
            max_overflow=10,
        )
    return _vector_engine


def _get_session_factory():
    global _vector_session_factory
    if _vector_session_factory is None:
        _vector_session_factory = async_sessionmaker(
            _get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _vector_session_factory


async def init_vector_db():
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("pgvector database initialized")


async def close_vector_db():
    global _vector_engine, _vector_session_factory
    if _vector_engine:
        await _vector_engine.dispose()
        _vector_engine = None
        _vector_session_factory = None


async def vector_insert(doc_id: str, text_content: str, embedding: list[float], metadata: dict[str, Any] | None = None):
    import json

    session_factory = _get_session_factory()
    async with session_factory() as session:
        doc = VectorDocument(
            id=doc_id,
            text=text_content,
            vector=embedding,
            metadata_=json.dumps(metadata, ensure_ascii=False) if metadata else None,
        )
        session.add(doc)
        await session.commit()


async def vector_delete(doc_id: str):
    session_factory = _get_session_factory()
    async with session_factory() as session:
        doc = await session.get(VectorDocument, doc_id)
        if doc:
            await session.delete(doc)
            await session.commit()


async def vector_search(embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
    import json

    session_factory = _get_session_factory()
    async with session_factory() as session:
        cosine_distance = VectorDocument.vector.cosine_distance(embedding)
        stmt = (
            select(VectorDocument, cosine_distance.label("distance"))
            .order_by(cosine_distance)
            .limit(top_k)
        )
        result = await session.execute(stmt)
        rows = result.all()

        results = []
        for doc, distance in rows:
            meta = json.loads(doc.metadata_) if doc.metadata_ else {}
            results.append({
                "id": doc.id,
                "text": doc.text,
                "score": 1 - distance,
                "metadata": meta,
            })
        return results
