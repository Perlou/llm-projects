"""
文档处理模块
处理文档加载、分块和索引
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import config


@dataclass
class ProcessedDocument:
    """处理后的文档"""

    doc_id: str
    filename: str
    file_type: str
    chunks: List[Document] = field(default_factory=list)


class DocumentProcessor:
    """文档处理器"""

    LOADERS = {
        ".pdf": PyPDFLoader,
        ".md": UnstructuredMarkdownLoader,
        ".txt": TextLoader,
    }

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", "。", ".", "！", "!", "？", "?", "；", ";", " "],
        )
        self.documents: Dict[str, ProcessedDocument] = {}

    def process_file(self, file_path: str) -> ProcessedDocument:
        """处理单个文件"""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext not in self.LOADERS:
            raise ValueError(f"不支持的文件格式: {ext}")

        # 加载文档
        loader_class = self.LOADERS[ext]
        if ext == ".txt":
            loader = loader_class(str(path), encoding="utf-8")
        else:
            loader = loader_class(str(path))

        raw_docs = loader.load()

        # 分块
        chunks = self.splitter.split_documents(raw_docs)

        # 添加元数据
        doc_id = path.stem
        for i, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "doc_id": doc_id,
                    "filename": path.name,
                    "chunk_id": f"{doc_id}_{i}",
                    "chunk_index": i,
                }
            )

        processed = ProcessedDocument(
            doc_id=doc_id,
            filename=path.name,
            file_type=ext[1:].upper(),
            chunks=chunks,
        )

        self.documents[doc_id] = processed
        return processed

    def process_directory(self, dir_path: str = None) -> List[ProcessedDocument]:
        """处理目录中的所有文档"""
        dir_path = dir_path or config.docs_dir
        path = Path(dir_path)

        if not path.exists():
            os.makedirs(path)
            return []

        processed = []
        for ext in self.LOADERS.keys():
            for file_path in path.glob(f"*{ext}"):
                try:
                    doc = self.process_file(str(file_path))
                    processed.append(doc)
                except Exception as e:
                    print(f"  ⚠️  处理失败 {file_path.name}: {e}")

        return processed

    def get_all_chunks(self) -> List[Document]:
        """获取所有文档块"""
        all_chunks = []
        for doc in self.documents.values():
            all_chunks.extend(doc.chunks)
        return all_chunks

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_chunks = sum(len(doc.chunks) for doc in self.documents.values())
        return {
            "total_documents": len(self.documents),
            "total_chunks": total_chunks,
            "documents": [
                {"name": doc.filename, "type": doc.file_type, "chunks": len(doc.chunks)}
                for doc in self.documents.values()
            ],
        }
