"""
BM25 检索器模块
基于词频的关键词检索
"""

import re
from typing import List, Tuple
from dataclasses import dataclass

import jieba
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

from config import config


@dataclass
class BM25Result:
    """BM25 检索结果"""

    document: Document
    score: float
    rank: int


class BM25Retriever:
    """BM25 检索器"""

    def __init__(self):
        self.documents: List[Document] = []
        self.tokenized_docs: List[List[str]] = []
        self.bm25: BM25Okapi = None

    def _tokenize(self, text: str) -> List[str]:
        """分词（支持中英文）"""
        # 英文转小写
        text = text.lower()

        # 中文分词
        tokens = list(jieba.cut(text))

        # 过滤停用词和短词
        tokens = [t.strip() for t in tokens if len(t.strip()) > 1]

        return tokens

    def build_index(self, documents: List[Document]):
        """构建 BM25 索引"""
        self.documents = documents
        self.tokenized_docs = [self._tokenize(doc.page_content) for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)

    def search(self, query: str, top_k: int = None) -> List[BM25Result]:
        """搜索"""
        if not self.bm25:
            return []

        top_k = top_k or config.bm25_top_k

        # 分词查询
        tokenized_query = self._tokenize(query)

        # 获取分数
        scores = self.bm25.get_scores(tokenized_query)

        # 排序并获取 top_k
        scored_docs = list(zip(self.documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        results = []
        for rank, (doc, score) in enumerate(scored_docs[:top_k], 1):
            if score > 0:  # 只返回有匹配的结果
                results.append(BM25Result(document=doc, score=score, rank=rank))

        return results

    def get_doc_count(self) -> int:
        """获取文档数量"""
        return len(self.documents)
