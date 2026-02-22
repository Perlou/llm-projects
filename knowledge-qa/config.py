"""
配置管理模块
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """应用配置"""

    # API 配置
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # 模型配置
    llm_model: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")

    # RAG 参数
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    top_k: int = int(os.getenv("TOP_K", "5"))

    # 路径配置
    docs_dir: str = os.path.join(os.path.dirname(__file__), "docs")
    data_dir: str = os.path.join(os.path.dirname(__file__), "data")
    collection_name: str = "knowledge_base"

    def validate(self) -> bool:
        """验证配置"""
        if not self.google_api_key:
            print("❌ 错误: 请设置 GOOGLE_API_KEY 环境变量")
            return False
        return True


# 全局配置实例
config = Config()
