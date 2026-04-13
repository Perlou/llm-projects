"""
多模态搜索
==========

实现图文混合搜索功能。

支持:
    - 文本搜索图片
    - 图片搜索图片
    - 多模态内容索引
"""

import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

import google.generativeai as genai
from PIL import Image

from config import config

# 尝试导入 ChromaDB
try:
    import chromadb
    from chromadb.config import Settings

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None


@dataclass
class SearchResult:
    """搜索结果"""

    id: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    image_path: Optional[str] = None


class MultimodalSearch:
    """多模态搜索引擎"""

    def __init__(self, collection_name: str = "multimodal"):
        """
        初始化搜索引擎

        Args:
            collection_name: 向量集合名称
        """
        genai.configure(api_key=config.google_api_key)
        self.model = genai.GenerativeModel(config.gemini_model)

        if not CHROMA_AVAILABLE:
            raise RuntimeError("需要安装 chromadb: pip install chromadb")

        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(config.vector_store_dir),
            settings=Settings(anonymized_telemetry=False),
        )

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _generate_image_description(self, image: Image.Image) -> str:
        """使用 Gemini 生成图像描述"""
        prompt = """详细描述这张图片，用于搜索索引。包括：
1. 主要内容
2. 场景和环境
3. 物体和颜色
4. 文字（如有）
5. 风格和氛围

用简洁的中文描述，每个方面一句话。"""

        response = self.model.generate_content([prompt, image])
        return response.text

    def _get_text_embedding(self, text: str) -> List[float]:
        """获取文本嵌入向量"""
        # 使用 Gemini embedding model
        result = genai.embed_content(
            model="gemini-embedding-001",
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]

    def _get_query_embedding(self, query: str) -> List[float]:
        """获取查询嵌入向量"""
        result = genai.embed_content(
            model="gemini-embedding-001",
            content=query,
            task_type="retrieval_query",
        )
        return result["embedding"]

    def _generate_image_id(self, image_path: str) -> str:
        """生成图片唯一 ID"""
        return hashlib.md5(image_path.encode()).hexdigest()[:16]

    def add_image(
        self,
        image_source: Union[str, Path, Image.Image],
        metadata: Optional[Dict[str, Any]] = None,
        custom_description: Optional[str] = None,
    ) -> str:
        """
        添加图片到索引

        Args:
            image_source: 图片路径或 PIL Image
            metadata: 元数据
            custom_description: 自定义描述（可选）

        Returns:
            图片 ID
        """
        # 加载图片
        if isinstance(image_source, Image.Image):
            image = image_source
            image_path = (
                metadata.get("path", "inline_image") if metadata else "inline_image"
            )
        else:
            image_path = str(image_source)
            image = Image.open(image_path)

        # 生成描述
        if custom_description:
            description = custom_description
        else:
            description = self._generate_image_description(image)

        # 生成嵌入
        embedding = self._get_text_embedding(description)

        # 生成 ID
        image_id = self._generate_image_id(image_path)

        # 准备元数据
        doc_metadata = {
            "path": image_path,
            "description": description,
            "type": "image",
        }
        if metadata:
            doc_metadata.update(metadata)

        # 添加到集合
        self.collection.add(
            ids=[image_id],
            embeddings=[embedding],
            metadatas=[doc_metadata],
            documents=[description],
        )

        return image_id

    def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        添加文本到索引

        Args:
            text: 文本内容
            metadata: 元数据

        Returns:
            文本 ID
        """
        # 生成嵌入
        embedding = self._get_text_embedding(text)

        # 生成 ID
        text_id = hashlib.md5(text.encode()).hexdigest()[:16]

        # 准备元数据
        doc_metadata = {
            "type": "text",
        }
        if metadata:
            doc_metadata.update(metadata)

        # 添加到集合
        self.collection.add(
            ids=[text_id],
            embeddings=[embedding],
            metadatas=[doc_metadata],
            documents=[text],
        )

        return text_id

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_type: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        文本搜索

        Args:
            query: 搜索查询
            top_k: 返回结果数量
            filter_type: 过滤类型 ("image", "text", None)

        Returns:
            搜索结果列表
        """
        # 生成查询嵌入
        query_embedding = self._get_query_embedding(query)

        # 构建过滤条件
        where = None
        if filter_type:
            where = {"type": filter_type}

        # 执行搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["metadatas", "documents", "distances"],
        )

        # 处理结果
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                document = results["documents"][0][i] if results["documents"] else ""

                # 转换距离为相似度分数
                score = 1 - distance

                search_results.append(
                    SearchResult(
                        id=doc_id,
                        score=score,
                        metadata=metadata,
                        description=document,
                        image_path=metadata.get("path")
                        if metadata.get("type") == "image"
                        else None,
                    )
                )

        return search_results

    def search_by_image(
        self,
        image_source: Union[str, Path, Image.Image],
        top_k: int = 5,
    ) -> List[SearchResult]:
        """
        以图搜图

        Args:
            image_source: 查询图片
            top_k: 返回结果数量

        Returns:
            搜索结果列表
        """
        # 加载图片
        if isinstance(image_source, Image.Image):
            image = image_source
        else:
            image = Image.open(str(image_source))

        # 生成图片描述
        description = self._generate_image_description(image)

        # 使用描述进行搜索
        return self.search(description, top_k=top_k, filter_type="image")

    def search_similar(
        self,
        doc_id: str,
        top_k: int = 5,
    ) -> List[SearchResult]:
        """
        搜索相似内容

        Args:
            doc_id: 文档 ID
            top_k: 返回结果数量

        Returns:
            相似结果列表（排除自身）
        """
        # 获取原文档
        result = self.collection.get(
            ids=[doc_id],
            include=["embeddings"],
        )

        if not result["embeddings"]:
            return []

        # 使用原文档嵌入搜索
        embedding = result["embeddings"][0]

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k + 1,  # 多取一个，排除自身
            include=["metadatas", "documents", "distances"],
        )

        # 处理结果，排除自身
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, result_id in enumerate(results["ids"][0]):
                if result_id == doc_id:
                    continue

                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                document = results["documents"][0][i] if results["documents"] else ""

                score = 1 - distance

                search_results.append(
                    SearchResult(
                        id=result_id,
                        score=score,
                        metadata=metadata,
                        description=document,
                        image_path=metadata.get("path")
                        if metadata.get("type") == "image"
                        else None,
                    )
                )

                if len(search_results) >= top_k:
                    break

        return search_results

    def delete(self, doc_id: str):
        """删除索引项"""
        self.collection.delete(ids=[doc_id])

    def clear(self):
        """清空索引"""
        # 删除并重建集合
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"},
        )

    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        count = self.collection.count()

        # 获取类型分布
        all_items = self.collection.get(include=["metadatas"])
        type_counts = {"image": 0, "text": 0}

        if all_items["metadatas"]:
            for metadata in all_items["metadatas"]:
                item_type = metadata.get("type", "unknown")
                type_counts[item_type] = type_counts.get(item_type, 0) + 1

        return {
            "total_count": count,
            "type_distribution": type_counts,
        }
