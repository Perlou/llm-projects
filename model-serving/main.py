"""
LLM 推理服务
==============

生产级 LLM 推理 API 服务
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from rich.console import Console

from app.config import settings
from app.api import router
from app.middleware import LoggingMiddleware, CORSMiddleware
from app.engine import get_engine


console = Console()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    console.print("\n[bold blue]🚀 LLM 推理服务[/bold blue]\n")
    console.print(f"模型: {settings.model_name}")
    console.print(f"引擎: {settings.inference_engine}")
    console.print("正在加载模型...")

    # 预加载模型
    try:
        engine = get_engine()
        console.print("[green]✅ 模型加载完成[/green]")
    except Exception as e:
        console.print(f"[red]模型加载失败: {e}[/red]")

    console.print(f"\n服务地址: http://{settings.host}:{settings.port}")
    console.print("API 文档: http://{settings.host}:{settings.port}/docs\n")

    yield

    console.print("\n[dim]服务关闭[/dim]")


# 创建应用
app = FastAPI(
    title="LLM 推理服务",
    description="生产级 LLM 推理 API，兼容 OpenAI 接口",
    version="1.0.0",
    lifespan=lifespan,
)

# 添加中间件
app.add_middleware(LoggingMiddleware)
app.add_middleware(CORSMiddleware)

# 注册路由
app.include_router(router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "LLM 推理服务",
        "version": "1.0.0",
        "model": settings.model_name,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=False,
    )
