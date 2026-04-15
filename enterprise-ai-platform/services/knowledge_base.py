"""
知识库管理服务
==============

支持多知识库的创建、管理和 RAG 问答。
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from config import config
from services.llm_provider import get_llm, get_embeddings


@dataclass
class KnowledgeBase:
    """知识库数据类"""

    id: str
    name: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    document_count: int = 0
    chunk_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeBase":
        return cls(**data)


@dataclass
class QueryResult:
    """查询结果"""

    answer: str
    sources: List[Dict[str, Any]]
    query: str


class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self):
        self.base_dir = config.knowledge_bases_dir
        self.embeddings = get_embeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "],
        )

    def _get_kb_dir(self, kb_id: str) -> Path:
        """获取知识库目录"""
        return self.base_dir / kb_id

    def _get_metadata_path(self, kb_id: str) -> Path:
        """获取元数据文件路径"""
        return self._get_kb_dir(kb_id) / "metadata.json"

    def _get_vectorstore(self, kb_id: str) -> Chroma:
        """获取向量存储"""
        persist_dir = self._get_kb_dir(kb_id) / "chroma_db"
        return Chroma(
            persist_directory=str(persist_dir),
            embedding_function=self.embeddings,
        )

    def list_knowledge_bases(self) -> List[KnowledgeBase]:
        """列出所有知识库"""
        kbs = []
        for kb_dir in self.base_dir.iterdir():
            if kb_dir.is_dir():
                metadata_path = kb_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path) as f:
                        data = json.load(f)
                        kbs.append(KnowledgeBase.from_dict(data))
        return sorted(kbs, key=lambda x: x.created_at, reverse=True)

    def create_knowledge_base(self, name: str, description: str = "") -> KnowledgeBase:
        """创建知识库"""
        # 生成 ID
        kb_id = f"kb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        kb_dir = self._get_kb_dir(kb_id)
        kb_dir.mkdir(parents=True, exist_ok=True)

        # 创建元数据
        kb = KnowledgeBase(
            id=kb_id,
            name=name,
            description=description,
        )

        # 保存元数据
        with open(self._get_metadata_path(kb_id), "w") as f:
            json.dump(kb.to_dict(), f, ensure_ascii=False, indent=2)

        return kb

    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        """获取知识库信息"""
        metadata_path = self._get_metadata_path(kb_id)
        if metadata_path.exists():
            with open(metadata_path) as f:
                return KnowledgeBase.from_dict(json.load(f))
        return None

    def delete_knowledge_base(self, kb_id: str) -> bool:
        """删除知识库"""
        kb_dir = self._get_kb_dir(kb_id)
        if kb_dir.exists():
            shutil.rmtree(kb_dir)
            return True
        return False

    def _load_document(self, file_path: Path) -> List[Document]:
        """加载文档"""
        suffix = file_path.suffix.lower()
        content = ""
        metadata = {"filename": file_path.name, "source": str(file_path)}

        if suffix == ".txt":
            content = file_path.read_text(encoding="utf-8")
        elif suffix == ".md":
            content = file_path.read_text(encoding="utf-8")
        elif suffix == ".pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(str(file_path))
                pages = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        pages.append(
                            Document(
                                page_content=text, metadata={**metadata, "page": i}
                            )
                        )
                return pages
            except ImportError:
                raise ImportError("请安装 pypdf: pip install pypdf")
        else:
            content = file_path.read_text(encoding="utf-8")

        return [Document(page_content=content, metadata=metadata)]

    def add_document(self, kb_id: str, file_path: Path) -> int:
        """添加文档到知识库"""
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            raise ValueError(f"知识库不存在: {kb_id}")

        # 加载文档
        docs = self._load_document(file_path)

        # 分割文档
        chunks = self.text_splitter.split_documents(docs)

        # 存入向量库
        vectorstore = self._get_vectorstore(kb_id)
        vectorstore.add_documents(chunks)

        # 更新元数据
        kb.document_count += 1
        kb.chunk_count += len(chunks)
        with open(self._get_metadata_path(kb_id), "w") as f:
            json.dump(kb.to_dict(), f, ensure_ascii=False, indent=2)

        return len(chunks)

    def add_text(self, kb_id: str, text: str, metadata: Optional[Dict] = None) -> int:
        """直接添加文本"""
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            raise ValueError(f"知识库不存在: {kb_id}")

        # 创建文档
        doc = Document(page_content=text, metadata=metadata or {})
        chunks = self.text_splitter.split_documents([doc])

        # 存入向量库
        vectorstore = self._get_vectorstore(kb_id)
        vectorstore.add_documents(chunks)

        # 更新元数据
        kb.chunk_count += len(chunks)
        with open(self._get_metadata_path(kb_id), "w") as f:
            json.dump(kb.to_dict(), f, ensure_ascii=False, indent=2)

        return len(chunks)

    def query(self, kb_id: str, question: str, top_k: int = None) -> QueryResult:
        """查询知识库"""
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            raise ValueError(f"知识库不存在: {kb_id}")

        top_k = top_k or config.top_k
        vectorstore = self._get_vectorstore(kb_id)

        # 检索相关文档
        docs = vectorstore.similarity_search(question, k=top_k)

        if not docs:
            return QueryResult(
                answer="抱歉，知识库中没有找到相关信息。",
                sources=[],
                query=question,
            )

        # 构建上下文
        context = "\n\n---\n\n".join(
            [
                f"[{i + 1}] {doc.metadata.get('filename', '未知来源')}\n{doc.page_content}"
                for i, doc in enumerate(docs)
            ]
        )

        # 生成回答
        prompt = ChatPromptTemplate.from_template("""你是一个专业的知识库助手。请根据提供的上下文信息回答用户问题。

规则：
1. 只根据上下文信息回答，不要编造内容
2. 如果上下文中没有相关信息，请明确告知用户
3. 回答要准确、简洁、有条理
4. 如果可以，请引用具体的来源

上下文信息：
{context}

用户问题：{question}

请回答：""")

        llm = get_llm(temperature=0.3)
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        # 提取来源
        sources = []
        seen = set()
        for doc in docs:
            filename = doc.metadata.get("filename", "未知")
            if filename not in seen:
                seen.add(filename)
                sources.append(
                    {
                        "filename": filename,
                        "page": doc.metadata.get("page"),
                        "preview": doc.page_content[:100] + "...",
                    }
                )

        return QueryResult(answer=answer, sources=sources, query=question)


# 全局实例
_manager: Optional[KnowledgeBaseManager] = None


def get_kb_manager() -> KnowledgeBaseManager:
    """获取知识库管理器实例"""
    global _manager
    if _manager is None:
        _manager = KnowledgeBaseManager()
    return _manager
