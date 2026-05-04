import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

_prompts: dict[str, str] = {}

_PROMPT_KEY_MAP = {
    "chat": "PROMPT_CHAT_DATA_ID",
    "route_agent": "PROMPT_ROUTE_AGENT_DATA_ID",
    "recommend_agent": "PROMPT_RECOMMEND_AGENT_DATA_ID",
    "buy_agent": "PROMPT_BUY_AGENT_DATA_ID",
    "consult_agent": "PROMPT_CONSULT_AGENT_DATA_ID",
    "knowledge_agent": "PROMPT_KNOWLEDGE_AGENT_DATA_ID",
    "text": "PROMPT_TEXT_DATA_ID",
}


def _load_from_file(data_id: str) -> str:
    file_path = _PROMPTS_DIR / data_id
    if file_path.exists():
        return file_path.read_text(encoding="utf-8").strip()
    return ""


def _load_from_nacos(data_id: str) -> str:
    try:
        import nacos

        from app.core.config import settings

        client = nacos.NacosClient(
            settings.NACOS_SERVER_ADDR,
            namespace=settings.NACOS_NAMESPACE,
            username=settings.NACOS_USERNAME,
            password=settings.NACOS_PASSWORD,
        )
        resp = client.get_config(data_id, settings.NACOS_GROUP)
        return resp.get("content", "").strip() if resp else ""
    except Exception as e:
        logger.warning("Failed to load prompt from Nacos: %s", e)
        return _load_from_file(data_id)


def load_all_prompts():
    from app.core.config import settings

    for key, config_key in _PROMPT_KEY_MAP.items():
        data_id = getattr(settings, config_key, "")
        if not data_id:
            continue
        if settings.NACOS_ENABLED:
            _prompts[key] = _load_from_nacos(data_id)
        else:
            _prompts[key] = _load_from_file(data_id)
        if not _prompts[key]:
            logger.warning("Prompt '%s' is empty (data_id=%s)", key, data_id)


def get_prompt(key: str) -> str:
    if not _prompts:
        load_all_prompts()
    return _prompts.get(key, "")


def reload_prompt(key: str):
    from app.core.config import settings

    config_key = _PROMPT_KEY_MAP.get(key)
    if not config_key:
        return
    data_id = getattr(settings, config_key, "")
    if not data_id:
        return
    if settings.NACOS_ENABLED:
        _prompts[key] = _load_from_nacos(data_id)
    else:
        _prompts[key] = _load_from_file(data_id)
