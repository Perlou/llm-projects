"""
文本分割器模块
智能分割文档为适合 RAG 的文本块
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import config


class TextSplitter:
    """文本分割器"""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or config.chunk_size
        self.chunk_overlap = chunk_overlap or config.chunk_overlap

        # 中英文混合的分隔符
        self.separators = [
            "\n\n",  # 段落
            "\n",  # 换行
            "。",  # 中文句号
            ".",  # 英文句号
            "！",
            "!",
            "？",
            "?",
            "；",
            ";",
            "，",
            ",",
            " ",  # 空格
            "",  # 字符级
        ]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档列表"""
        chunks = self.splitter.split_documents(documents)

        # 添加分块索引
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i

        return chunks

    def split_text(self, text: str) -> List[str]:
        """分割纯文本"""
        return self.splitter.split_text(text)

    def get_stats(self, chunks: List[Document]) -> dict:
        """获取分割统计"""
        if not chunks:
            return {"total_chunks": 0, "avg_length": 0}

        lengths = [len(chunk.page_content) for chunk in chunks]
        return {
            "total_chunks": len(chunks),
            "avg_length": sum(lengths) // len(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths),
        }
