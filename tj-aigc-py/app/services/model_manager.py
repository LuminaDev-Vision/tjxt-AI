import hashlib
import json
import logging
import time
from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.core.redis import get_redis

logger = logging.getLogger(__name__)

EXACT_CACHE_PREFIX = "model_cache:"
DEFAULT_TTL = 3600  # 1小时


class ModelConfig(BaseModel):
    """模型配置"""
    name: str
    temperature: float = 0.2
    max_tokens: int = 1000
    timeout: int = 30
    retry_count: int = 3


class ModelManager:
    """
    模型管理器 — 场景化模型配置 + 双层缓存（精确 + 语义）

    使用场景:
    - intent:   意图识别（低温度、少token）
    - general:  一般问答（中温度）
    - creative: 创意内容（高温度、多token）

    缓存策略:
    1. 精确匹配（MD5 key，零开销）
    2. 语义匹配（SemanticCache，相似问题命中）
    """

    _instance: "ModelManager | None" = None

    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._configs: dict[str, ModelConfig] = {}
        self._semantic_cache: "SemanticCache | None" = None
        self._init_defaults()

    def _init_defaults(self):
        defaults = {
            "intent": ModelConfig(
                name=settings.DASHSCOPE_MODEL,
                temperature=0.1,
                max_tokens=200,
            ),
            "general": ModelConfig(
                name=settings.DASHSCOPE_MODEL,
                temperature=0.2,
                max_tokens=1000,
            ),
            "creative": ModelConfig(
                name=settings.DASHSCOPE_MODEL,
                temperature=0.3,
                max_tokens=1500,
            ),
        }
        self._configs.update(defaults)

    @property
    def semantic_cache(self) -> "SemanticCache":
        if self._semantic_cache is None:
            from app.services.semantic_cache import SemanticCache
            self._semantic_cache = SemanticCache()
        return self._semantic_cache

    def register(self, scene: str, config: ModelConfig):
        """注册场景模型配置"""
        self._configs[scene] = config

    def get_config(self, scene: str) -> ModelConfig | None:
        """获取场景模型配置"""
        return self._configs.get(scene)

    # ---- 精确缓存（MD5 key） ----

    @staticmethod
    def _exact_key(prompt: str, scene: str) -> str:
        content = f"{prompt}:{scene}"
        return f"{EXACT_CACHE_PREFIX}{hashlib.md5(content.encode()).hexdigest()}"

    async def _get_exact(self, prompt: str, scene: str) -> str | None:
        try:
            r = get_redis()
            data = await r.get(self._exact_key(prompt, scene))
            if data:
                return json.loads(data)["response"]
        except Exception as e:
            logger.debug("Exact cache read error: %s", e)
        return None

    async def _set_exact(self, prompt: str, scene: str, response: str, ttl: int = DEFAULT_TTL):
        try:
            r = get_redis()
            data = json.dumps({"response": response, "ts": time.time()}, ensure_ascii=False)
            await r.setex(self._exact_key(prompt, scene), ttl, data)
        except Exception as e:
            logger.debug("Exact cache write error: %s", e)

    # ---- 语义缓存 ----

    async def _get_semantic(self, prompt: str) -> str | None:
        return await self.semantic_cache.get(prompt)

    async def _set_semantic(self, prompt: str, response: str):
        await self.semantic_cache.set(prompt, response)

    # ---- 生成入口 ----

    async def generate(
        self,
        prompt: str,
        scene: str = "general",
        system_prompt: str | None = None,
        use_cache: bool = True,
    ) -> str | None:
        """
        生成模型响应

        缓存查找顺序: 精确匹配 → 语义匹配 → LLM 调用
        """
        config = self._configs.get(scene)
        if not config:
            logger.warning("Unknown scene: %s", scene)
            return None

        if use_cache:
            # 1. 精确匹配
            cached = await self._get_exact(prompt, scene)
            if cached:
                logger.debug("Exact cache hit: scene=%s", scene)
                return cached

            # 2. 语义匹配
            cached = await self._get_semantic(prompt)
            if cached:
                logger.debug("Semantic cache hit: scene=%s", scene)
                # 回填精确缓存
                await self._set_exact(prompt, scene, cached)
                return cached

        # 3. LLM 调用
        start = time.time()
        response = await self._call_llm(prompt, config, system_prompt)
        elapsed = time.time() - start
        logger.info("LLM call: scene=%s, model=%s, %.2fs", scene, config.name, elapsed)

        if use_cache and response:
            await self._set_exact(prompt, scene, response)
            await self._set_semantic(prompt, response)

        return response

    async def _call_llm(
        self, prompt: str, config: ModelConfig, system_prompt: str | None
    ) -> str | None:
        """调用 LLM，支持重试"""
        from app.clients.dashscope_client import dashscope_chat

        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(config.retry_count):
            try:
                return await dashscope_chat(messages)
            except Exception as e:
                logger.warning("LLM call failed (attempt %d/%d): %s", attempt + 1, config.retry_count, e)
                if attempt == config.retry_count - 1:
                    return None
        return None

    async def clear_cache(self, scene: str | None = None):
        """清空缓存（精确 + 语义）"""
        r = get_redis()
        try:
            if scene:
                keys = await r.keys(f"{EXACT_CACHE_PREFIX}*")
                if keys:
                    await r.delete(*keys)
            else:
                exact_keys = await r.keys(f"{EXACT_CACHE_PREFIX}*")
                if exact_keys:
                    await r.delete(*exact_keys)
                await self.semantic_cache.clear()
            logger.info("Cache cleared")
        except Exception as e:
            logger.warning("Cache clear error: %s", e)


model_manager = ModelManager()
