"""
向量检索器模块
基于语义相似度的向量检索
"""

import os
from typing import List, Tuple
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from config import config


@dataclass
class VectorResult:
    """向量检索结果"""

    document: Document
    score: float  # 相似度分数 (0-1)
    rank: int


class VectorRetriever:
    """向量检索器"""

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.embedding_model,
            google_api_key=config.google_api_key,
        )

        os.makedirs(config.data_dir, exist_ok=True)

        self.vectorstore = Chroma(
            collection_name="enterprise_search",
            embedding_function=self.embeddings,
            persist_directory=config.data_dir,
        )

    def build_index(self, documents: List[Document]):
        """构建向量索引"""
        if documents:
            self.vectorstore.add_documents(documents)

    def search(self, query: str, top_k: int = None) -> List[VectorResult]:
        """向量检索"""
        top_k = top_k or config.vector_top_k

        # 带分数的相似度搜索
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query=query,
            k=top_k,
        )

        vector_results = []
        for rank, (doc, score) in enumerate(results, 1):
            vector_results.append(VectorResult(document=doc, score=score, rank=rank))

        return vector_results

    def clear(self):
        """清空索引"""
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            collection_name="enterprise_search",
            embedding_function=self.embeddings,
            persist_directory=config.data_dir,
        )

    def get_doc_count(self) -> int:
        """获取文档数量"""
        return self.vectorstore._collection.count()
