"""
RAG 引擎模块
实现检索增强生成的核心逻辑
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from config import config
from vector_store import VectorStore


@dataclass
class RAGResponse:
    """RAG 响应结果"""

    answer: str
    sources: List[Dict[str, Any]]
    query: str


class RAGEngine:
    """RAG 引擎"""

    SYSTEM_PROMPT = """你是一个专业的知识库助手。请根据提供的上下文信息回答用户问题。

规则：
1. 只根据上下文信息回答，不要编造内容
2. 如果上下文中没有相关信息，请明确告知用户
3. 回答要准确、简洁、有条理
4. 如果可以，请引用具体的来源

上下文信息：
{context}
"""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = ChatGoogleGenerativeAI(
            model=config.llm_model,
            temperature=0.7,
            google_api_key=config.google_api_key,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

    def _format_docs(self, docs: List[Document]) -> str:
        """格式化检索到的文档"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("filename", "未知来源")
            page = doc.metadata.get("page", "")
            page_info = f" (第 {page + 1} 页)" if page != "" else ""

            formatted.append(f"[{i}] 来源: {source}{page_info}\n{doc.page_content}")

        return "\n\n---\n\n".join(formatted)

    def _extract_sources(self, docs: List[Document]) -> List[Dict[str, Any]]:
        """提取来源信息"""
        sources = []
        seen = set()

        for doc in docs:
            source = doc.metadata.get("filename", "未知")
            page = doc.metadata.get("page", None)
            key = f"{source}:{page}"

            if key not in seen:
                seen.add(key)
                sources.append(
                    {
                        "filename": source,
                        "page": page + 1 if page is not None else None,
                        "content_preview": doc.page_content[:100] + "...",
                    }
                )

        return sources

    def query(
        self,
        question: str,
        chat_history: List = None,
    ) -> RAGResponse:
        """执行 RAG 查询"""
        chat_history = chat_history or []

        # 1. 检索相关文档
        docs = self.vector_store.search(question, k=config.top_k)

        if not docs:
            return RAGResponse(
                answer="抱歉，知识库中没有找到相关信息。请确保已添加相关文档。",
                sources=[],
                query=question,
            )

        # 2. 格式化上下文
        context = self._format_docs(docs)

        # 3. 构建并执行链
        chain = self.prompt | self.llm | StrOutputParser()

        answer = chain.invoke(
            {
                "context": context,
                "question": question,
                "chat_history": chat_history,
            }
        )

        # 4. 提取来源
        sources = self._extract_sources(docs)

        return RAGResponse(
            answer=answer,
            sources=sources,
            query=question,
        )

    def get_relevant_docs(self, query: str) -> List[Document]:
        """获取相关文档（用于调试）"""
        return self.vector_store.search(query, k=config.top_k)
