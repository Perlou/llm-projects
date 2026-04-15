"""
知识库 API 路由
===============

知识库管理相关的 REST API 端点。
"""

import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from config import config
from services.knowledge_base import get_kb_manager


router = APIRouter(prefix="/api/knowledge", tags=["知识库"])


# ==================== 数据模型 ====================


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""

    name: str = Field(..., description="知识库名称")
    description: str = Field("", description="知识库描述")


class KnowledgeBaseInfo(BaseModel):
    """知识库信息"""

    id: str
    name: str
    description: str
    document_count: int
    chunk_count: int
    created_at: str


class QueryRequest(BaseModel):
    """查询请求"""

    question: str = Field(..., description="查询问题")
    top_k: int = Field(5, ge=1, le=20, description="返回文档数量")


class QueryResponse(BaseModel):
    """查询响应"""

    answer: str
    sources: List[dict]
    query: str


class AddTextRequest(BaseModel):
    """添加文本请求"""

    text: str = Field(..., description="文本内容")
    metadata: dict = Field(default_factory=dict, description="元数据")


# ==================== API 端点 ====================


@router.get("", response_model=List[KnowledgeBaseInfo])
async def list_knowledge_bases():
    """获取所有知识库列表"""
    manager = get_kb_manager()
    kbs = manager.list_knowledge_bases()

    return [
        KnowledgeBaseInfo(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            document_count=kb.document_count,
            chunk_count=kb.chunk_count,
            created_at=kb.created_at,
        )
        for kb in kbs
    ]


@router.post("", response_model=KnowledgeBaseInfo)
async def create_knowledge_base(request: KnowledgeBaseCreate):
    """
    创建新知识库

    - **name**: 知识库名称
    - **description**: 知识库描述
    """
    manager = get_kb_manager()
    kb = manager.create_knowledge_base(request.name, request.description)

    return KnowledgeBaseInfo(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        document_count=kb.document_count,
        chunk_count=kb.chunk_count,
        created_at=kb.created_at,
    )


@router.get("/{kb_id}", response_model=KnowledgeBaseInfo)
async def get_knowledge_base(kb_id: str):
    """获取知识库详情"""
    manager = get_kb_manager()
    kb = manager.get_knowledge_base(kb_id)

    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    return KnowledgeBaseInfo(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        document_count=kb.document_count,
        chunk_count=kb.chunk_count,
        created_at=kb.created_at,
    )


@router.delete("/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """删除知识库"""
    manager = get_kb_manager()

    if not manager.get_knowledge_base(kb_id):
        raise HTTPException(status_code=404, detail="知识库不存在")

    success = manager.delete_knowledge_base(kb_id)
    return {"success": success}


@router.post("/{kb_id}/documents")
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
):
    """
    上传文档到知识库

    支持的格式: PDF, TXT, MD
    """
    manager = get_kb_manager()

    if not manager.get_knowledge_base(kb_id):
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 保存上传的文件
    upload_dir = config.uploads_dir
    file_path = upload_dir / file.filename

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 添加到知识库
        chunk_count = manager.add_document(kb_id, file_path)

        return {
            "success": True,
            "filename": file.filename,
            "chunk_count": chunk_count,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 清理临时文件
        if file_path.exists():
            file_path.unlink()


@router.post("/{kb_id}/text")
async def add_text(kb_id: str, request: AddTextRequest):
    """
    直接添加文本到知识库

    - **text**: 文本内容
    - **metadata**: 可选的元数据
    """
    manager = get_kb_manager()

    if not manager.get_knowledge_base(kb_id):
        raise HTTPException(status_code=404, detail="知识库不存在")

    try:
        chunk_count = manager.add_text(kb_id, request.text, request.metadata)
        return {"success": True, "chunk_count": chunk_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_id}/query", response_model=QueryResponse)
async def query_knowledge_base(kb_id: str, request: QueryRequest):
    """
    查询知识库

    - **question**: 查询问题
    - **top_k**: 返回的文档数量
    """
    manager = get_kb_manager()

    if not manager.get_knowledge_base(kb_id):
        raise HTTPException(status_code=404, detail="知识库不存在")

    try:
        result = manager.query(kb_id, request.question, top_k=request.top_k)

        return QueryResponse(
            answer=result.answer,
            sources=result.sources,
            query=result.query,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
