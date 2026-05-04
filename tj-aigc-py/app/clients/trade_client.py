import httpx

from app.core.config import settings


async def pre_place_order(course_ids: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{settings.TRADE_SERVICE_URL}/orders/prePlaceOrder",
            params={"courseIds": course_ids},
        )
        resp.raise_for_status()
        return resp.json()
