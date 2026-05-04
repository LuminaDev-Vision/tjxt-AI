from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.enums import ChatEventTypeEnum


class ChatDTO(BaseModel):
    question: str
    session_id: str


class ChatEventVO(BaseModel):
    event_data: Any = Field(alias="eventData")
    event_type: int = Field(alias="eventType")

    model_config = {"populate_by_name": True}


STOP_EVENT = ChatEventVO(event_data="", event_type=ChatEventTypeEnum.STOP)


class TemplateVO(BaseModel):
    associational_word: Optional[str] = Field(default=None, alias="associationalWord")
    helped_write: Optional[str] = Field(default=None, alias="helpedWrite")
    continued_write: Optional[str] = Field(default=None, alias="continuedWrite")
    polish: Optional[str] = Field(default=None, alias="polish")
    streamline: Optional[str] = Field(default=None, alias="streamline")

    model_config = {"populate_by_name": True}
