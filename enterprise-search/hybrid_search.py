"""
混合检索模块
结合 BM25 和向量检索，使用 RRF 算法融合
"""

from typing import List, Dict, Set
from dataclasses import dataclass

from langchain_core.documents import Document

from config import config
from bm25_retriever import BM25Retriever, BM25Result
from vector_retriever import VectorRetriever, VectorResult


@dataclass
class HybridResult:
    """混合检索结果"""

    document: Document
    rrf_score: float
    bm25_rank: int = 0
    vector_rank: int = 0
    sources: List[str] = None

    def __post_init__(self):
        self.sources = []
        if self.bm25_rank > 0:
            self.sources.append("BM25")
        if self.vector_rank > 0:
            self.sources.append("Vector")


class HybridSearcher:
    """混合检索器"""

    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        vector_retriever: VectorRetriever,
    ):
        self.bm25 = bm25_retriever
        self.vector = vector_retriever
        self.rrf_k = config.rrf_k

    def search(
        self,
        query: str,
        bm25_k: int = None,
        vector_k: int = None,
    ) -> List[HybridResult]:
        """执行混合检索"""
        bm25_k = bm25_k or config.bm25_top_k
        vector_k = vector_k or config.vector_top_k

        # 并行检索
        bm25_results = self.bm25.search(query, bm25_k)
        vector_results = self.vector.search(query, vector_k)

        # RRF 融合
        return self._rrf_fusion(bm25_results, vector_results)

    def _rrf_fusion(
        self,
        bm25_results: List[BM25Result],
        vector_results: List[VectorResult],
    ) -> List[HybridResult]:
        """
        Reciprocal Rank Fusion (RRF) 算法
        score = sum(1 / (k + rank)) for each result list
        """
        # 使用 chunk_id 作为唯一标识
        doc_scores: Dict[str, Dict] = {}

        # 处理 BM25 结果
        for result in bm25_results:
            chunk_id = result.document.metadata.get("chunk_id", id(result.document))
            if chunk_id not in doc_scores:
                doc_scores[chunk_id] = {
                    "document": result.document,
                    "rrf_score": 0,
                    "bm25_rank": 0,
                    "vector_rank": 0,
                }
            doc_scores[chunk_id]["bm25_rank"] = result.rank
            doc_scores[chunk_id]["rrf_score"] += 1 / (self.rrf_k + result.rank)

        # 处理向量结果
        for result in vector_results:
            chunk_id = result.document.metadata.get("chunk_id", id(result.document))
            if chunk_id not in doc_scores:
                doc_scores[chunk_id] = {
                    "document": result.document,
                    "rrf_score": 0,
                    "bm25_rank": 0,
                    "vector_rank": 0,
                }
            doc_scores[chunk_id]["vector_rank"] = result.rank
            doc_scores[chunk_id]["rrf_score"] += 1 / (self.rrf_k + result.rank)

        # 转换为结果列表并排序
        hybrid_results = [
            HybridResult(
                document=data["document"],
                rrf_score=data["rrf_score"],
                bm25_rank=data["bm25_rank"],
                vector_rank=data["vector_rank"],
            )
            for data in doc_scores.values()
        ]

        hybrid_results.sort(key=lambda x: x.rrf_score, reverse=True)
        return hybrid_results

    def get_search_stats(
        self,
        bm25_results: List[BM25Result],
        vector_results: List[VectorResult],
        hybrid_results: List[HybridResult],
    ) -> Dict:
        """获取检索统计"""
        return {
            "bm25_count": len(bm25_results),
            "vector_count": len(vector_results),
            "hybrid_count": len(hybrid_results),
            "overlap": len(
                set(r.document.metadata.get("chunk_id") for r in bm25_results)
                & set(r.document.metadata.get("chunk_id") for r in vector_results)
            ),
        }
