"""
多模态内容分析平台 - API 服务
==============================

基于 FastAPI 的 REST API 服务。
"""

import io
import base64
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from PIL import Image

from config import config
from analyzers import ImageAnalyzer, ChartAnalyzer, VideoAnalyzer, AudioAnalyzer
from search import MultimodalSearch


# ==================== 数据模型 ====================


class AnalysisResponse(BaseModel):
    """分析响应"""

    success: bool
    data: dict
    message: str = ""


class SearchRequest(BaseModel):
    """搜索请求"""

    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    filter_type: Optional[str] = None


class SearchResultItem(BaseModel):
    """搜索结果项"""

    id: str
    score: float
    description: str
    image_path: Optional[str] = None
    metadata: dict = {}


class SearchResponse(BaseModel):
    """搜索响应"""

    success: bool
    results: List[SearchResultItem]
    total: int


# ==================== 全局实例 ====================

image_analyzer: Optional[ImageAnalyzer] = None
chart_analyzer: Optional[ChartAnalyzer] = None
video_analyzer: Optional[VideoAnalyzer] = None
audio_analyzer: Optional[AudioAnalyzer] = None
search_engine: Optional[MultimodalSearch] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global image_analyzer, chart_analyzer, video_analyzer, audio_analyzer, search_engine

    # 启动时初始化
    if not config.validate():
        raise RuntimeError("配置验证失败，请检查 GOOGLE_API_KEY")

    print("🚀 初始化分析器...")
    image_analyzer = ImageAnalyzer()
    chart_analyzer = ChartAnalyzer()
    video_analyzer = VideoAnalyzer()
    audio_analyzer = AudioAnalyzer()

    try:
        search_engine = MultimodalSearch()
        print("✅ 搜索引擎已初始化")
    except Exception as e:
        print(f"⚠️  搜索引擎初始化失败: {e}")

    print("✅ 服务就绪")

    yield

    # 关闭时清理
    print("👋 服务关闭")


# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="多模态内容分析 API",
    description="基于 Gemini 的多模态内容理解与分析服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 健康检查 ====================


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "model": config.gemini_model}


# ==================== 图像分析 ====================


@app.post("/api/analyze/image", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    task: str = Form(default="describe"),
    detail_level: str = Form(default="detailed"),
):
    """
    分析图像

    - **file**: 图片文件
    - **task**: 任务类型 (describe, extract_text, detect_objects, analyze_full)
    - **detail_level**: 详细程度 (brief, detailed, comprehensive)
    """
    try:
        # 读取图片
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # 执行分析
        if task == "describe":
            result = image_analyzer.describe(image, detail_level=detail_level)
            data = {"description": result.description}
        elif task == "extract_text":
            result = image_analyzer.extract_text(image)
            data = {"text": result.text}
        elif task == "detect_objects":
            result = image_analyzer.detect_objects(image)
            data = {"objects": result.objects}
        elif task == "analyze_full":
            result = image_analyzer.analyze_full(image)
            data = {
                "description": result.description,
                "objects": result.objects,
                "text": result.text,
                "scene": result.scene,
                "colors": result.colors,
            }
        else:
            raise HTTPException(status_code=400, detail=f"未知任务类型: {task}")

        return AnalysisResponse(success=True, data=data)

    except Exception as e:
        return AnalysisResponse(success=False, data={}, message=str(e))


# ==================== 图表分析 ====================


@app.post("/api/analyze/chart", response_model=AnalysisResponse)
async def analyze_chart(
    file: UploadFile = File(...),
    output_format: str = Form(default="json"),
):
    """
    分析图表

    - **file**: 图表图片
    - **output_format**: 输出格式 (json, markdown)
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        result = chart_analyzer.analyze(image)

        data = {
            "chart_type": result.chart_type,
            "title": result.title,
            "data": result.data,
            "x_axis": result.x_axis,
            "y_axis": result.y_axis,
            "legend": result.legend,
            "statistics": result.statistics,
            "trend": result.trend,
            "insights": result.insights,
        }

        return AnalysisResponse(success=True, data=data)

    except Exception as e:
        return AnalysisResponse(success=False, data={}, message=str(e))


@app.post("/api/analyze/chart/trend", response_model=AnalysisResponse)
async def analyze_chart_trend(
    file: UploadFile = File(...),
    context: str = Form(default=""),
):
    """
    分析图表趋势

    - **file**: 图表图片
    - **context**: 背景信息
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        analysis = chart_analyzer.analyze_trend(image, context=context)

        return AnalysisResponse(success=True, data={"analysis": analysis})

    except Exception as e:
        return AnalysisResponse(success=False, data={}, message=str(e))


# ==================== 视频分析 ====================


@app.post("/api/analyze/video", response_model=AnalysisResponse)
async def analyze_video(
    file: UploadFile = File(...),
    max_frames: int = Form(default=10),
):
    """
    分析视频

    - **file**: 视频文件
    - **max_frames**: 最大分析帧数
    """
    try:
        # 保存临时文件
        import tempfile

        temp_path = tempfile.mktemp(suffix=Path(file.filename).suffix)
        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        result = video_analyzer.summarize(temp_path, num_frames=max_frames)

        # 清理临时文件
        Path(temp_path).unlink(missing_ok=True)

        data = {
            "summary": result.summary,
            "duration": result.duration,
            "key_frames": result.key_frames,
            "scenes": result.scenes,
        }

        return AnalysisResponse(success=True, data=data)

    except Exception as e:
        return AnalysisResponse(success=False, data={}, message=str(e))


# ==================== 音频分析 ====================


@app.post("/api/analyze/audio", response_model=AnalysisResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    language: str = Form(default="zh"),
):
    """
    分析音频

    - **file**: 音频文件
    - **language**: 语言代码 (zh, en)
    """
    try:
        import tempfile

        temp_path = tempfile.mktemp(suffix=Path(file.filename).suffix)
        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        result = audio_analyzer.analyze(temp_path, language=language)

        Path(temp_path).unlink(missing_ok=True)

        data = {
            "transcript": result.transcript,
            "summary": result.summary,
            "keywords": result.keywords,
            "topics": result.topics,
            "duration": result.duration,
        }

        return AnalysisResponse(success=True, data=data)

    except Exception as e:
        return AnalysisResponse(success=False, data={}, message=str(e))


@app.post("/api/analyze/audio/meeting", response_model=AnalysisResponse)
async def analyze_meeting(
    file: UploadFile = File(...),
    language: str = Form(default="zh"),
):
    """
    分析会议录音

    - **file**: 会议录音文件
    - **language**: 语言代码
    """
    try:
        import tempfile

        temp_path = tempfile.mktemp(suffix=Path(file.filename).suffix)
        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        result = audio_analyzer.meeting_analysis(temp_path, language=language)

        Path(temp_path).unlink(missing_ok=True)

        data = {
            "transcript": result.transcript,
            "summary": result.summary,
            "action_items": result.action_items,
            "topics": result.topics,
            "metadata": result.metadata,
        }

        return AnalysisResponse(success=True, data=data)

    except Exception as e:
        return AnalysisResponse(success=False, data={}, message=str(e))


# ==================== 多模态搜索 ====================


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    多模态搜索

    - **query**: 搜索查询
    - **top_k**: 返回结果数量
    - **filter_type**: 过滤类型 (image, text)
    """
    if not search_engine:
        raise HTTPException(status_code=503, detail="搜索引擎未初始化")

    try:
        results = search_engine.search(
            query=request.query,
            top_k=request.top_k,
            filter_type=request.filter_type,
        )

        items = [
            SearchResultItem(
                id=r.id,
                score=r.score,
                description=r.description,
                image_path=r.image_path,
                metadata=r.metadata,
            )
            for r in results
        ]

        return SearchResponse(success=True, results=items, total=len(items))

    except Exception as e:
        return SearchResponse(success=False, results=[], total=0)


@app.post("/api/search/index/image")
async def index_image(
    file: UploadFile = File(...),
    description: str = Form(default=""),
    category: str = Form(default=""),
):
    """
    添加图片到搜索索引

    - **file**: 图片文件
    - **description**: 自定义描述
    - **category**: 分类标签
    """
    if not search_engine:
        raise HTTPException(status_code=503, detail="搜索引擎未初始化")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        metadata = {"filename": file.filename}
        if category:
            metadata["category"] = category

        image_id = search_engine.add_image(
            image,
            metadata=metadata,
            custom_description=description if description else None,
        )

        return {"success": True, "id": image_id}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/search/stats")
async def search_stats():
    """获取搜索索引统计"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="搜索引擎未初始化")

    return search_engine.get_stats()


# ==================== 运行服务 ====================


def main():
    """启动服务"""
    import uvicorn

    print("\n🖼️  多模态内容分析 API 服务")
    print("━" * 40)
    print(f"📖 API 文档: http://localhost:8000/docs")
    print(f"🔧 模型: {config.gemini_model}")
    print("━" * 40 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
