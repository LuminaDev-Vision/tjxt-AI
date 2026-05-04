from enum import Enum, IntEnum


class AgentTypeEnum(str, Enum):
    ROUTE = "ROUTE"
    RECOMMEND = "RECOMMEND"
    CONSULT = "CONSULT"
    BUY = "BUY"
    KNOWLEDGE = "KNOWLEDGE"

    @classmethod
    def from_name(cls, name: str) -> "AgentTypeEnum | None":
        try:
            return cls(name.strip().upper())
        except ValueError:
            return None


class ChatEventTypeEnum(IntEnum):
    DATA = 1001
    STOP = 1002
    PARAM = 1003


class MessageTypeEnum(IntEnum):
    USER = 1
    ASSISTANT = 2
