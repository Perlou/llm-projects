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

    # 检索参数
    bm25_top_k: int = int(os.getenv("BM25_TOP_K", "20"))
    vector_top_k: int = int(os.getenv("VECTOR_TOP_K", "20"))
    rerank_top_n: int = int(os.getenv("RERANK_TOP_N", "5"))
    rrf_k: int = int(os.getenv("RRF_K", "60"))

    # 文本处理
    chunk_size: int = 500
    chunk_overlap: int = 100

    # 路径
    docs_dir: str = os.path.join(os.path.dirname(__file__), "docs")
    data_dir: str = os.path.join(os.path.dirname(__file__), "data")

    # Reranker
    reranker_model: str = os.getenv("RERANKER_MODEL", "")
    use_llm_reranker: bool = True  # 使用 LLM 作为 reranker

    def validate(self) -> bool:
        """验证配置"""
        if not self.google_api_key:
            print("❌ 错误: 请设置 GOOGLE_API_KEY 环境变量")
            return False
        return True


config = Config()
