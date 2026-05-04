from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class SessionVO(BaseModel):
    session_id: str
    title: str
    describe: str
    examples: list[str]


class ChatSessionVO(BaseModel):
    session_id: str
    title: Optional[str] = None
    update_time: datetime


class MessageVO(BaseModel):
    type: int
    content: Optional[str] = None
    params: Optional[dict[str, Any]] = None


class SessionHistoryVO(BaseModel):
    group: str
    sessions: list[ChatSessionVO]
