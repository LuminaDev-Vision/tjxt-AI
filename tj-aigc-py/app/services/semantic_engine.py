import hashlib
import logging
import math
import re
from abc import ABC, abstractmethod
from collections import Counter

logger = logging.getLogger(__name__)


class SimilarityStrategy(ABC):
    """相似度计算策略"""

    @abstractmethod
    def calculate(self, text1: str, text2: str) -> float: ...


class CharCosineStrategy(SimilarityStrategy):
    """字符级 n-gram 余弦相似度（零依赖，内置兜底）"""

    def __init__(self, n: int = 2):
        self.n = n

    def _get_ngrams(self, text: str) -> list[str]:
        return [text[i : i + self.n] for i in range(len(text) - self.n + 1)]

    def calculate(self, text1: str, text2: str) -> float:
        ngrams1 = self._get_ngrams(text1)
        ngrams2 = self._get_ngrams(text2)
        if not ngrams1 or not ngrams2:
            return 0.0

        vec1 = Counter(ngrams1)
        vec2 = Counter(ngrams2)
        all_keys = set(vec1) | set(vec2)

        dot = sum(vec1[k] * vec2[k] for k in all_keys)
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)


class TFIDFStrategy(SimilarityStrategy):
    """TF-IDF + 余弦相似度（需 sklearn + jieba）"""

    def calculate(self, text1: str, text2: str) -> float:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        try:
            import jieba

            tokenizer = lambda t: list(jieba.cut(t))
        except ImportError:
            tokenizer = None

        vectorizer = TfidfVectorizer(
            tokenizer=tokenizer,
            lowercase=tokenizer is None,
            ngram_range=(1, 2),
            max_features=1000,
        )
        matrix = vectorizer.fit_transform([text1, text2])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])


class SemanticEngine:
    """
    语义引擎 — 相似度计算 + 模板识别 + 问题提取

    策略自动降级：TF-IDF → 字符余弦 → 精确匹配
    """

    def __init__(self, strategy: str = "tfidf"):
        self._strategies: dict[str, SimilarityStrategy] = {
            "tfidf": TFIDFStrategy(),
            "char_cosine": CharCosineStrategy(),
        }
        self._primary = strategy
        self._fallback = "char_cosine" if strategy == "tfidf" else "tfidf"

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的语义相似度 (0.0 ~ 1.0)"""
        for name in (self._primary, self._fallback):
            try:
                return self._strategies[name].calculate(text1, text2)
            except ImportError:
                logger.debug("Strategy '%s' unavailable, falling back", name)
                continue
            except Exception as e:
                logger.warning("Strategy '%s' error: %s", name, e)
                continue
        # 最终兜底：精确匹配
        return 1.0 if text1 == text2 else 0.0

    @staticmethod
    def extract_user_question(prompt: str) -> str:
        """从 prompt 中提取用户问题部分"""
        patterns = [
            r"用户问题[：:]\s*(.+?)(?:\n|$)",
            r"用户输入[：:]\s*(.+?)(?:\n|$)",
            r"问题[：:]\s*(.+?)(?:\n|$)",
            r"Human[：:]\s*(.+?)(?:\n|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip().strip("\"'")
        return ""

    @staticmethod
    def identify_template(prompt: str) -> str:
        """
        识别 prompt 模板类型 — 取前 200 字符哈希作为模板 ID。
        相同模板的 prompt 结构一致，只是变量不同。
        """
        static_part = prompt[:200]
        return hashlib.md5(static_part.encode()).hexdigest()[:12]
