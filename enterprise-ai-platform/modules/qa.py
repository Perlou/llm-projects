"""
智能问答模块
============

基于知识库的智能问答功能。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from services.knowledge_base import get_kb_manager, KnowledgeBase, QueryResult
from services.llm_provider import get_llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


@dataclass
class QAResponse:
    """问答响应"""

    answer: str
    sources: List[Dict[str, Any]]
    query: str
    rewritten_query: Optional[str] = None
    confidence: float = 0.0


class QAModule:
    """智能问答模块"""

    def __init__(self):
        self.kb_manager = get_kb_manager()

    def rewrite_query(self, query: str) -> str:
        """查询改写，优化检索效果"""
        llm = get_llm(temperature=0.3)
        prompt = ChatPromptTemplate.from_template("""请将用户的问题改写为更适合检索的形式。
保持原意的同时，补充可能的同义词或相关术语。

原始问题: {query}

改写后的问题（只输出改写结果，不要其他内容）:""")

        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"query": query})

    def query(
        self,
        question: str,
        kb_id: Optional[str] = None,
        rewrite: bool = False,
        top_k: int = 5,
    ) -> QAResponse:
        """执行问答"""
        # 选择知识库
        if kb_id:
            kb = self.kb_manager.get_knowledge_base(kb_id)
            if not kb:
                return QAResponse(
                    answer=f"知识库不存在: {kb_id}",
                    sources=[],
                    query=question,
                )
        else:
            kbs = self.kb_manager.list_knowledge_bases()
            if not kbs:
                return QAResponse(
                    answer="没有可用的知识库，请先创建并添加文档。",
                    sources=[],
                    query=question,
                )
            kb = kbs[0]

        # 查询改写
        search_query = question
        rewritten = None
        if rewrite:
            rewritten = self.rewrite_query(question)
            search_query = rewritten

        # 执行查询
        result = self.kb_manager.query(kb.id, search_query, top_k=top_k)

        return QAResponse(
            answer=result.answer,
            sources=result.sources,
            query=question,
            rewritten_query=rewritten,
        )

    def multi_kb_query(
        self,
        question: str,
        kb_ids: List[str] = None,
        top_k: int = 5,
    ) -> QAResponse:
        """跨多个知识库查询"""
        # 获取知识库列表
        if kb_ids:
            kbs = [self.kb_manager.get_knowledge_base(id) for id in kb_ids]
            kbs = [kb for kb in kbs if kb]
        else:
            kbs = self.kb_manager.list_knowledge_bases()

        if not kbs:
            return QAResponse(
                answer="没有可用的知识库。",
                sources=[],
                query=question,
            )

        # 从每个知识库检索
        all_sources = []
        all_contexts = []

        for kb in kbs:
            result = self.kb_manager.query(kb.id, question, top_k=top_k // len(kbs) + 1)
            for source in result.sources:
                source["kb_name"] = kb.name
            all_sources.extend(result.sources)

        # 综合生成答案
        context = "\n\n---\n\n".join(
            [f"[{s['filename']}] {s.get('preview', '')}" for s in all_sources[:top_k]]
        )

        llm = get_llm(temperature=0.3)
        prompt = ChatPromptTemplate.from_template("""根据以下来自多个知识库的信息，回答用户问题。

信息:
{context}

问题: {question}

回答:""")

        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        return QAResponse(
            answer=answer,
            sources=all_sources[:top_k],
            query=question,
        )


# 便捷函数
def quick_qa(question: str, kb_id: str = None) -> str:
    """快速问答"""
    module = QAModule()
    result = module.query(question, kb_id=kb_id)
    return result.answer
