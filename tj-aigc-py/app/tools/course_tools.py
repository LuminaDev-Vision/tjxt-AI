from typing import Any

import httpx

from app.core.config import settings
from app.tools.base import ToolResultHolder

COURSE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "queryCourseById",
            "description": "根据课程ID查询课程详情，包括课程名称、价格、有效期、学习人数、课程详情等信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "courseId": {"type": "integer", "description": "课程ID"}
                },
                "required": ["courseId"],
            },
        },
    }
]


async def query_course_by_id(course_id: int, request_id: str = "") -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{settings.COURSE_SERVICE_URL}/courses/baseInfo/{course_id}")
        resp.raise_for_status()
        data = resp.json()

    course_info = {
        "id": data.get("id"),
        "name": data.get("name"),
        "price": data.get("price", 0) / 100,
        "validDuration": data.get("validDuration"),
        "usePeople": data.get("usePeople"),
        "detail": data.get("detail"),
    }

    if request_id:
        ToolResultHolder.put(request_id, "courseInfo", course_info)

    return course_info
