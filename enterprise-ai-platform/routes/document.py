"""
文档处理 API 路由
=================

文档处理相关的 REST API 端点。
"""

from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from config import config
from modules.document import DocumentProcessor


router = APIRouter(prefix="/api/document", tags=["文档处理"])


# ==================== 数据模型 ====================


class SummarizeRequest(BaseModel):
    """摘要请求"""

    text: str = Field(..., description="文本内容")
    style: str = Field("detailed", description="摘要风格: brief 或 detailed")


class SummaryResponse(BaseModel):
    """摘要响应"""

    title: str
    summary: str
    key_points: List[str]
    keywords: List[str]


class ExtractRequest(BaseModel):
    """提取请求"""

    text: str = Field(..., description="文本内容")
    extract_types: List[str] = Field(
        default=["人名", "地名", "组织", "日期"], description="要提取的信息类型"
    )


class ExtractResponse(BaseModel):
    """提取响应"""

    entities: dict
    facts: List[str]


class CompareRequest(BaseModel):
    """比较请求"""

    text1: str = Field(..., description="文档1内容")
    text2: str = Field(..., description="文档2内容")


# ==================== API 端点 ====================


processor = DocumentProcessor()


@router.post("/summarize", response_model=SummaryResponse)
async def summarize_text(request: SummarizeRequest):
    """
    生成文本摘要

    - **text**: 待摘要的文本
    - **style**: 摘要风格 (brief: 简短, detailed: 详细)
    """
    try:
        result = processor.summarize(request.text, style=request.style)
        return SummaryResponse(
            title=result.title,
            summary=result.summary,
            key_points=result.key_points,
            keywords=result.keywords,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize/file", response_model=SummaryResponse)
async def summarize_file(
    file: UploadFile = File(...),
    style: str = "detailed",
):
    """
    上传文件并生成摘要

    支持的格式: PDF, TXT, MD
    """
    try:
        # 保存临时文件
        temp_path = config.uploads_dir / file.filename
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 加载并处理
        doc = processor.load_document(temp_path)
        result = processor.summarize(doc.content, style=style)

        # 清理临时文件
        temp_path.unlink(missing_ok=True)

        return SummaryResponse(
            title=result.title,
            summary=result.summary,
            key_points=result.key_points,
            keywords=result.keywords,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract", response_model=ExtractResponse)
async def extract_info(request: ExtractRequest):
    """
    从文本中提取结构化信息

    - **text**: 待提取的文本
    - **extract_types**: 要提取的信息类型列表
    """
    try:
        result = processor.extract_info(request.text, request.extract_types)
        return ExtractResponse(
            entities=result.entities,
            facts=result.facts,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_documents(request: CompareRequest):
    """
    比较两个文档

    - **text1**: 文档1内容
    - **text2**: 文档2内容
    """
    try:
        comparison = processor.compare_documents(request.text1, request.text2)
        return {"comparison": comparison}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
