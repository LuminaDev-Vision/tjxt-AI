import json
import logging
import time

from app.core.redis import get_redis
from app.services.semantic_engine import SemanticEngine

logger = logging.getLogger(__name__)

CACHE_PREFIX = "semantic:"
DEFAULT_TTL = 10800  # 3小时
MAX_ENTRIES_PER_TEMPLATE = 50


class SemanticCache:
    """
    语义缓存 — 基于语义相似度的 Redis 智能缓存

    存储结构（Redis Hash）:
        key:   semantic:{template_id}
        field: {prompt_hash}
        value: {"prompt": str, "response": str, "ts": float}

    查找流程:
        1. 用 SemanticEngine.identify_template 定位模板
        2. 遍历该模板下所有缓存条目
        3. 用 SemanticEngine 计算相似度，超过阈值则命中
    """

    def __init__(
        self,
        engine: SemanticEngine | None = None,
        similarity_threshold: float = 0.8,
        ttl: int = DEFAULT_TTL,
    ):
        self.engine = engine or SemanticEngine()
        self.threshold = similarity_threshold
        self.ttl = ttl

    @staticmethod
    def _redis_key(template_id: str) -> str:
        return f"{CACHE_PREFIX}{template_id}"

    async def get(self, prompt: str) -> str | None:
        """
        语义匹配获取缓存。
        遍历同模板条目，找到相似度 >= 阈值的最新有效响应。
        """
        template_id = self.engine.identify_template(prompt)
        user_question = self.engine.extract_user_question(prompt)
        compare_text = user_question if user_question else prompt

        r = get_redis()
        key = self._redis_key(template_id)

        try:
            entries = await r.hgetall(key)
        except Exception as e:
            logger.warning("Semantic cache read error: %s", e)
            return None

        if not entries:
            return None

        now = time.time()
        best_score = 0.0
        best_response = None

        for _field, raw in entries.items():
            try:
                entry = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue

            # 过期检查
            if now - entry.get("ts", 0) > self.ttl:
                continue

            cached_question = entry.get("question", entry.get("prompt", ""))
            if not cached_question:
                continue

            score = self.engine.calculate_similarity(compare_text, cached_question)
            if score >= self.threshold and score > best_score:
                best_score = score
                best_response = entry.get("response")

        if best_response:
            logger.info("Semantic cache hit: template=%s, score=%.2f", template_id, best_score)
        return best_response

    async def set(self, prompt: str, response: str):
        """存储响应到语义缓存"""
        template_id = self.engine.identify_template(prompt)
        user_question = self.engine.extract_user_question(prompt)
        prompt_hash = self.engine.identify_template(prompt + response)[:8]

        r = get_redis()
        key = self._redis_key(template_id)

        entry = json.dumps(
            {
                "prompt": prompt,
                "question": user_question or prompt,
                "response": response,
                "ts": time.time(),
            },
            ensure_ascii=False,
        )

        try:
            await r.hset(key, prompt_hash, entry)
            await r.expire(key, self.ttl)

            # 限制条目数量
            count = await r.hlen(key)
            if count > MAX_ENTRIES_PER_TEMPLATE:
                all_fields = await r.hkeys(key)
                # 按 field 删除多余的（简单策略：删最旧的一半）
                to_remove = all_fields[: count - MAX_ENTRIES_PER_TEMPLATE // 2]
                if to_remove:
                    await r.hdel(key, *to_remove)
                    logger.debug("Evicted %d stale entries from template %s", len(to_remove), template_id)
        except Exception as e:
            logger.warning("Semantic cache write error: %s", e)

    async def clear(self):
        """清空所有语义缓存"""
        r = get_redis()
        try:
            keys = await r.keys(f"{CACHE_PREFIX}*")
            if keys:
                await r.delete(*keys)
                logger.info("Cleared %d semantic cache entries", len(keys))
        except Exception as e:
            logger.warning("Semantic cache clear error: %s", e)
