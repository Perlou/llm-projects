"""
文档加载器模块
支持 PDF、Markdown、TXT 等格式
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document


@dataclass
class LoadedDocument:
    """加载的文档信息"""

    filename: str
    file_type: str
    num_pages: int
    documents: List[Document]


class DocumentLoader:
    """文档加载器"""

    SUPPORTED_EXTENSIONS = {
        ".pdf": "PDF",
        ".md": "Markdown",
        ".txt": "Text",
    }

    def __init__(self):
        self.loaded_files: Dict[str, LoadedDocument] = {}

    def load_file(self, file_path: str) -> LoadedDocument:
        """加载单个文件"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {ext}")

        # 根据文件类型选择加载器
        if ext == ".pdf":
            loader = PyPDFLoader(str(path))
        elif ext == ".md":
            loader = UnstructuredMarkdownLoader(str(path))
        else:  # .txt
            loader = TextLoader(str(path), encoding="utf-8")

        documents = loader.load()

        # 添加元数据
        for doc in documents:
            doc.metadata["source"] = str(path)
            doc.metadata["filename"] = path.name
            doc.metadata["file_type"] = self.SUPPORTED_EXTENSIONS[ext]

        loaded_doc = LoadedDocument(
            filename=path.name,
            file_type=self.SUPPORTED_EXTENSIONS[ext],
            num_pages=len(documents),
            documents=documents,
        )

        self.loaded_files[str(path)] = loaded_doc
        return loaded_doc

    def load_directory(self, dir_path: str) -> List[LoadedDocument]:
        """加载目录中的所有文档"""
        path = Path(dir_path)

        if not path.exists():
            os.makedirs(path)
            return []

        loaded = []
        for ext in self.SUPPORTED_EXTENSIONS.keys():
            for file_path in path.glob(f"*{ext}"):
                try:
                    doc = self.load_file(str(file_path))
                    loaded.append(doc)
                except Exception as e:
                    print(f"  ⚠️  加载失败 {file_path.name}: {e}")

        return loaded

    def get_all_documents(self) -> List[Document]:
        """获取所有已加载的文档"""
        all_docs = []
        for loaded_doc in self.loaded_files.values():
            all_docs.extend(loaded_doc.documents)
        return all_docs

    def get_stats(self) -> Dict[str, Any]:
        """获取加载统计"""
        return {
            "total_files": len(self.loaded_files),
            "files": [
                {
                    "name": doc.filename,
                    "type": doc.file_type,
                    "pages": doc.num_pages,
                }
                for doc in self.loaded_files.values()
            ],
        }
