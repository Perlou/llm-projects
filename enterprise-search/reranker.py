"""
重排序模块
使用 LLM 或 Cross-Encoder 进行语义重排序
"""

from typing import List
from dataclasses import dataclass

import google.generativeai as genai
from langchain_core.documents import Document

from config import config
from hybrid_search import HybridResult


@dataclass
class RerankedResult:
    """重排序结果"""

    document: Document
    relevance_score: float
    original_rank: int
    new_rank: int


class Reranker:
    """重排序器"""

    RERANK_PROMPT = """请评估以下文档与查询的相关性，给出 0-100 的相关度分数。

查询: {query}

文档内容:
{content}

请只返回一个数字（0-100），表示相关度分数。分数越高表示越相关。

相关度分数:"""

    def __init__(self):
        genai.configure(api_key=config.google_api_key)
        self.model = genai.GenerativeModel(config.llm_model)

    def rerank(
        self,
        query: str,
        results: List[HybridResult],
        top_n: int = None,
    ) -> List[RerankedResult]:
        """重排序"""
        top_n = top_n or config.rerank_top_n

        if not results:
            return []

        # 限制重排序的数量（避免 API 调用过多）
        candidates = results[: min(len(results), top_n * 2)]

        scored_results = []
        for i, result in enumerate(candidates):
            score = self._score_document(query, result.document.page_content)
            scored_results.append(
                {
                    "document": result.document,
                    "relevance_score": score,
                    "original_rank": i + 1,
                }
            )

        # 按分数排序
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)

        # 构建结果
        reranked = []
        for new_rank, item in enumerate(scored_results[:top_n], 1):
            reranked.append(
                RerankedResult(
                    document=item["document"],
                    relevance_score=item["relevance_score"],
                    original_rank=item["original_rank"],
                    new_rank=new_rank,
                )
            )

        return reranked

    def _score_document(self, query: str, content: str) -> float:
        """使用 LLM 评分"""
        try:
            # 截断内容
            max_len = 500
            if len(content) > max_len:
                content = content[:max_len] + "..."

            response = self.model.generate_content(
                self.RERANK_PROMPT.format(query=query, content=content),
                generation_config=genai.GenerationConfig(
                    temperature=0,
                    max_output_tokens=10,
                ),
            )

            score_text = response.text.strip()
            # 提取数字
            score = float("".join(c for c in score_text if c.isdigit() or c == "."))
            return min(100, max(0, score))

        except Exception as e:
            print(f"评分失败: {e}")
            return 50.0  # 默认分数
