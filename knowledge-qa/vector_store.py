"""
向量存储模块
使用 ChromaDB 进行向量存储和检索
"""

import os
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from config import config


class VectorStore:
    """向量存储管理器"""

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.embedding_model,
            google_api_key=config.google_api_key,
        )

        # 确保数据目录存在
        os.makedirs(config.data_dir, exist_ok=True)

        self.vectorstore: Optional[Chroma] = None
        self._load_or_create()

    def _load_or_create(self):
        """加载或创建向量存储"""
        self.vectorstore = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embeddings,
            persist_directory=config.data_dir,
        )

    def add_documents(self, documents: List[Document]) -> int:
        """添加文档到向量存储"""
        if not documents:
            return 0

        self.vectorstore.add_documents(documents)
        return len(documents)

    def search(
        self,
        query: str,
        k: int = None,
        filter: Dict[str, Any] = None,
    ) -> List[Document]:
        """相似度搜索"""
        k = k or config.top_k
        results = self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter,
        )
        return results

    def search_with_scores(
        self,
        query: str,
        k: int = None,
    ) -> List[tuple]:
        """带分数的相似度搜索"""
        k = k or config.top_k
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
        )
        return results

    def delete_by_source(self, source: str):
        """根据来源删除文档"""
        # ChromaDB 需要先获取 IDs 再删除
        results = self.vectorstore.get(
            where={"source": source},
        )
        if results and results["ids"]:
            self.vectorstore.delete(ids=results["ids"])

    def clear(self):
        """清空向量存储"""
        self.vectorstore.delete_collection()
        self._load_or_create()

    def get_stats(self) -> dict:
        """获取存储统计"""
        collection = self.vectorstore._collection
        return {
            "total_documents": collection.count(),
            "collection_name": config.collection_name,
        }
