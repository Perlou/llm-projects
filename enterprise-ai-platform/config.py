"""
配置管理
========

集中管理应用配置，支持 Gemini 和 Ollama 多模型切换。
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Literal

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class Config:
    """应用配置"""

    # API 配置
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))

    # 模型配置
    llm_provider: Literal["gemini", "ollama"] = field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini")
    )
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    )
    ollama_model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    )
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )

    # Embedding 配置
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    )

    # 路径配置
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent)

    @property
    def data_dir(self) -> Path:
        """数据目录"""
        path = self.base_dir / "data"
        path.mkdir(exist_ok=True)
        return path

    @property
    def knowledge_bases_dir(self) -> Path:
        """知识库目录"""
        path = self.data_dir / "knowledge_bases"
        path.mkdir(exist_ok=True)
        return path

    @property
    def uploads_dir(self) -> Path:
        """上传文件目录"""
        path = self.data_dir / "uploads"
        path.mkdir(exist_ok=True)
        return path

    # RAG 配置
    chunk_size: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000"))
    )
    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200"))
    )
    top_k: int = field(default_factory=lambda: int(os.getenv("TOP_K", "5")))

    # 服务配置
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))

    def validate(self) -> bool:
        """验证配置"""
        if self.llm_provider == "gemini" and not self.google_api_key:
            print("❌ 错误: 使用 Gemini 需要设置 GOOGLE_API_KEY")
            print("   获取地址: https://aistudio.google.com/apikey")
            return False
        return True

    def get_model_info(self) -> str:
        """获取当前模型信息"""
        if self.llm_provider == "gemini":
            return f"Gemini ({self.gemini_model})"
        else:
            return f"Ollama ({self.ollama_model})"


# 全局配置实例
config = Config()
