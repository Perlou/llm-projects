"""配置：从 .env 读取 LLM / 高德 / FastAPI 设置"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置"""

    # LLM
    llm_model_id: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_timeout: int = 120

    # 高德 MCP
    amap_maps_api_key: str = ""

    # FastAPI
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [s.strip() for s in self.app_cors_origins.split(",") if s.strip()]

    def assert_ready(self) -> None:
        """启动时校验关键配置"""
        missing: list[str] = []
        if not self.llm_model_id:
            missing.append("LLM_MODEL_ID")
        if not self.llm_api_key:
            missing.append("LLM_API_KEY")
        if not self.llm_base_url:
            missing.append("LLM_BASE_URL")
        if not self.amap_maps_api_key:
            missing.append("AMAP_MAPS_API_KEY")
        if missing:
            raise RuntimeError(
                "缺少环境变量：" + ", ".join(missing) + "。请复制 .env.example 为 .env 并填写。"
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
