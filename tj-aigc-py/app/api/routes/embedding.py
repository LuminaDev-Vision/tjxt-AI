from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def save_document(text: str, metadata: dict | None = None):
    from app.services.embedding_service import EmbeddingService

    svc = EmbeddingService()
    return await svc.save(text, metadata)


@router.delete("")
async def delete_document(doc_id: str):
    from app.services.embedding_service import EmbeddingService

    svc = EmbeddingService()
    await svc.delete(doc_id)


@router.get("/search")
async def search(query: str, top_k: int = 5):
    from app.services.embedding_service import EmbeddingService

    svc = EmbeddingService()
    return await svc.search(query, top_k)
