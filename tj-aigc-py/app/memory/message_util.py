from typing import Any


def to_user_message(content: str) -> dict[str, Any]:
    return {"messageType": "USER", "textContent": content}


def to_assistant_message(content: str, params: dict | None = None) -> dict[str, Any]:
    msg: dict[str, Any] = {"messageType": "ASSISTANT", "textContent": content}
    if params:
        msg["params"] = params
    return msg


def to_system_message(content: str) -> dict[str, Any]:
    return {"messageType": "SYSTEM", "textContent": content}


def to_tool_message(tool_call_id: str, content: str) -> dict[str, Any]:
    return {
        "messageType": "TOOL",
        "textContent": content,
        "toolResponses": [{"toolCallId": tool_call_id, "content": content}],
    }


def to_dashscope_messages(history: list[dict]) -> list[dict[str, Any]]:
    messages = []
    for msg in history:
        msg_type = msg.get("messageType", "")
        if msg_type == "USER":
            messages.append({"role": "user", "content": msg.get("textContent", "")})
        elif msg_type == "ASSISTANT":
            messages.append({"role": "assistant", "content": msg.get("textContent", "")})
        elif msg_type == "SYSTEM":
            messages.append({"role": "system", "content": msg.get("textContent", "")})
        elif msg_type == "TOOL":
            tool_responses = msg.get("toolResponses", [])
            for resp in tool_responses:
                messages.append({
                    "role": "tool",
                    "tool_call_id": resp.get("toolCallId", ""),
                    "content": resp.get("content", ""),
                })
    return messages
