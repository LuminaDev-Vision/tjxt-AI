import httpx

from app.core.config import settings


async def get_course_base_info(course_id: int) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{settings.COURSE_SERVICE_URL}/courses/baseInfo/{course_id}")
        resp.raise_for_status()
        return resp.json()
