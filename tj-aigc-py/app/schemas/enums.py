from enum import Enum, IntEnum


class AgentTypeEnum(str, Enum):
    ROUTE = ("ROUTE", "路由智能体")
    RECOMMEND = ("RECOMMEND", "课程推荐智能体")
    CONSULT = ("CONSULT", "课程咨询智能体")
    BUY = ("BUY", "课程购买智能体")
    KNOWLEDGE = ("KNOWLEDGE", "知识讲解智能体")

    def __init__(self, value: str, desc: str):
        self._value_ = value
        self.agent_name = value
        self.desc = desc

    def __str__(self):
        return self.name

    @classmethod
    def from_name(cls, name: str) -> "AgentTypeEnum | None":
        try:
            return cls(name.strip().upper())
        except ValueError:
            return None


class ChatEventTypeEnum(IntEnum):
    DATA = (1001, "数据事件")
    STOP = (1002, "停止事件")
    PARAM = (1003, "参数事件")

    def __init__(self, value: int, desc: str):
        self._value_ = value
        self.desc = desc

    def __str__(self):
        return self.name


class MessageTypeEnum(IntEnum):
    USER = (1, "用户提问")
    ASSISTANT = (2, "助手回复")

    def __init__(self, value: int, desc: str):
        self._value_ = value
        self.desc = desc

    def __str__(self):
        return self.name
