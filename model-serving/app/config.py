"""
配置管理模块
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 模型配置
    model_name: str = Field(default="Qwen/Qwen2.5-0.5B-Instruct")
    model_path: Optional[str] = Field(default=None)

    # 推理引擎
    inference_engine: str = Field(default="transformers")

    # 服务配置
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=1)

    # 推理参数
    max_new_tokens: int = Field(default=512)
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.9)

    # 性能配置
    max_batch_size: int = Field(default=8)
    max_concurrent_requests: int = Field(default=100)
    timeout_seconds: int = Field(default=60)

    # 量化
    load_in_8bit: bool = Field(default=False)
    load_in_4bit: bool = Field(default=False)

    # GPU
    device_map: str = Field(default="auto")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
