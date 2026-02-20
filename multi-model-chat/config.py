"""
配置文件
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """模型配置"""

    name: str
    provider: str
    model_id: str
    max_tokens: int = 1000
    temperature: float = 0.7
    # 价格（每 1K tokens，美元）
    input_price: float = 0.0
    output_price: float = 0.0


# 预定义模型配置
MODELS = {
    # OpenAI
    "gpt-4": ModelConfig(
        name="GPT-4",
        provider="openai",
        model_id="gpt-4",
        input_price=0.03,
        output_price=0.06,
    ),
    "gpt-4o": ModelConfig(
        name="GPT-4o",
        provider="openai",
        model_id="gpt-4o",
        input_price=0.005,
        output_price=0.015,
    ),
    "gpt-3.5-turbo": ModelConfig(
        name="GPT-3.5 Turbo",
        provider="openai",
        model_id="gpt-3.5-turbo",
        input_price=0.0005,
        output_price=0.0015,
    ),
    # Claude
    "claude-3-opus": ModelConfig(
        name="Claude 3 Opus",
        provider="anthropic",
        model_id="claude-3-opus-20240229",
        input_price=0.015,
        output_price=0.075,
    ),
    "claude-3-sonnet": ModelConfig(
        name="Claude 3.5 Sonnet",
        provider="anthropic",
        model_id="claude-3-5-sonnet-20241022",
        input_price=0.003,
        output_price=0.015,
    ),
    "claude-3-haiku": ModelConfig(
        name="Claude 3 Haiku",
        provider="anthropic",
        model_id="claude-3-haiku-20240307",
        input_price=0.00025,
        output_price=0.00125,
    ),
    # Gemini
    "gemini-pro": ModelConfig(
        name="Gemini 1.5 Pro",
        provider="gemini",
        model_id="gemini-1.5-pro",
        input_price=0.00125,
        output_price=0.005,
    ),
    "gemini-flash": ModelConfig(
        name="Gemini 1.5 Flash",
        provider="gemini",
        model_id="gemini-2.0-flash",
        input_price=0.000075,
        output_price=0.0003,
    ),
    # Ollama (本地)
    "llama3": ModelConfig(
        name="Llama 3.1 8B",
        provider="ollama",
        model_id="llama3.1",
        input_price=0.0,
        output_price=0.0,
    ),
    "qwen": ModelConfig(
        name="Qwen 2.5 7B",
        provider="ollama",
        model_id="qwen2.5",
        input_price=0.0,
        output_price=0.0,
    ),
}


def get_api_key(provider: str) -> Optional[str]:
    """获取 API Key"""
    keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GOOGLE_API_KEY"),
    }
    return keys.get(provider)


def get_default_models() -> list[str]:
    """获取默认启用的模型"""
    default = os.getenv("DEFAULT_MODELS", "gpt-3.5-turbo")
    return [m.strip() for m in default.split(",")]


def get_ollama_host() -> str:
    """获取 Ollama 地址"""
    return os.getenv("OLLAMA_HOST", "http://localhost:11434")
