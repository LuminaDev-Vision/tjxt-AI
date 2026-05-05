from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.utils.snowflake import snowflake


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_session"

    id: Optional[int] = Field(default_factory=snowflake.next_id, primary_key=True)
    session_id: str = Field(max_length=64, index=True)
    user_id: int = Field(index=True)
    title: Optional[str] = Field(default=None, max_length=100)
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)
    creater: Optional[int] = None
    updater: Optional[int] = None
