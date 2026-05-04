from typing import Any

import httpx

from app.core.config import settings
from app.tools.base import ToolResultHolder

ORDER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "prePlaceOrder",
            "description": "根据课程ID列表预下单，获取订单详情包括课程数量、总金额、优惠金额、优惠券名称、实付金额、订单ID等",
            "parameters": {
                "type": "object",
                "properties": {
                    "courseIds": {
                        "type": "string",
                        "description": "课程ID列表，多个用逗号分隔，如: 1,2,3",
                    }
                },
                "required": ["courseIds"],
            },
        },
    }
]


async def pre_place_order(course_ids: str, request_id: str = "") -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{settings.TRADE_SERVICE_URL}/orders/prePlaceOrder",
            params={"courseIds": course_ids},
        )
        resp.raise_for_status()
        data = resp.json()

    order_info = {
        "count": data.get("count"),
        "totalAmount": data.get("totalAmount", 0) / 100,
        "discountAmount": data.get("discountAmount", 0) / 100,
        "couponName": data.get("couponName"),
        "payAmount": data.get("payAmount", 0) / 100,
        "courseIds": data.get("courseIds"),
        "orderId": data.get("orderId"),
        "couponId": data.get("couponId"),
    }

    if request_id:
        ToolResultHolder.put(request_id, "orderInfo", order_info)

    return order_info
