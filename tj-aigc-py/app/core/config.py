from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_DIR = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ---- 应用 ----
    APP_NAME: str = "tj-aigc-py"
    APP_PORT: int = 8094
    DEBUG: bool = False

    # ---- MySQL ----
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "tj_aigc"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # ---- Redis ----
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ---- DashScope ----
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_MODEL: str = "qwen-plus"

    # ---- OpenAI ----
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_STT_MODEL: str = "whisper-1"

    # ---- pgvector (PostgreSQL) ----
    PGVECTOR_HOST: str = "localhost"
    PGVECTOR_PORT: int = 5432
    PGVECTOR_USER: str = "postgres"
    PGVECTOR_PASSWORD: str = "postgres"
    PGVECTOR_DB: str = "tj_aigc_vectors"

    @property
    def PGVECTOR_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PGVECTOR_USER}:{self.PGVECTOR_PASSWORD}@{self.PGVECTOR_HOST}:{self.PGVECTOR_PORT}/{self.PGVECTOR_DB}"

    EMBEDDING_MODEL: str = "text-embedding-v3"
    EMBEDDING_DIMS: int = 1536

    # ---- Session 配置 ----
    SESSION_TITLE: str = "天机学堂AI助手"
    SESSION_DESCRIBE: str = "我是天机学堂的AI助手，有什么可以帮您的？"

    # ---- 微服务地址 ----
    COURSE_SERVICE_URL: str = "http://localhost:8082"
    TRADE_SERVICE_URL: str = "http://localhost:8088"

    # ---- 鉴权 ----
    AUTH_HEADER_NAME: str = "Authorization"


settings = Settings()
