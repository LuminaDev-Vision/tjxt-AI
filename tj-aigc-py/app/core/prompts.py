import logging
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


class PromptKey(str, Enum):
    CHAT = "chat"
    ROUTE_AGENT = "route_agent"
    RECOMMEND_AGENT = "recommend_agent"
    BUY_AGENT = "buy_agent"
    CONSULT_AGENT = "consult_agent"
    KNOWLEDGE_AGENT = "knowledge_agent"
    TEXT = "text"

    @property
    def file_name(self) -> str:
        return self.value.replace("_", "-") + "-system-message.txt"


class PromptManager:
    _instance: "PromptManager | None" = None
    _prompts: dict[str, str] = {}

    def __new__(cls) -> "PromptManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_all(self):
        for key in PromptKey:
            file_path = _PROMPTS_DIR / key.file_name
            if file_path.exists():
                self._prompts[key.value] = file_path.read_text(encoding="utf-8").strip()
            else:
                logger.warning("Prompt file not found: %s", file_path)
                self._prompts[key.value] = ""

    def get(self, key: PromptKey, **kwargs: str) -> str:
        if not self._prompts:
            self.load_all()
        template = self._prompts.get(key.value, "")
        if kwargs and template:
            return self._render(template, kwargs)
        return template

    def reload(self, key: PromptKey):
        file_path = _PROMPTS_DIR / key.file_name
        if file_path.exists():
            self._prompts[key.value] = file_path.read_text(encoding="utf-8").strip()

    @staticmethod
    def _render(template: str, variables: dict[str, str]) -> str:
        result = template
        for k, v in variables.items():
            result = result.replace(f"{{{k}}}", v)
        return result


prompt_manager = PromptManager()
