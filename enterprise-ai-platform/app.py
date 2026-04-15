"""
企业级 AI 平台 - FastAPI 应用
==============================

REST API 服务入口。
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import config
from routes import chat, knowledge, document


# ==================== 应用生命周期 ====================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时验证配置
    if not config.validate():
        print("⚠️  配置验证失败，部分功能可能不可用")

    print(f"🚀 企业级 AI 平台启动")
    print(f"📡 模型: {config.get_model_info()}")
    print(f"📖 API 文档: http://{config.api_host}:{config.api_port}/docs")

    yield

    print("👋 服务关闭")


# ==================== FastAPI 应用 ====================


app = FastAPI(
    title="企业级 AI 平台",
    description="""
综合性 AI 服务平台，提供：
- 🤖 智能对话服务
- 📚 知识库管理和问答
- 📄 文档处理和分析
- 🔧 工作流自动化

基于 Gemini/Ollama 多模型支持。
    """,
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

# 注册路由
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(document.router)


# ==================== 基础端点 ====================


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "企业级 AI 平台",
        "version": "1.0.0",
        "model": config.get_model_info(),
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "model": config.get_model_info(),
        "provider": config.llm_provider,
    }


@app.get("/api/stats")
async def get_stats():
    """获取平台统计信息"""
    from services.knowledge_base import get_kb_manager
    from services.chat import get_chat_service

    kb_manager = get_kb_manager()
    chat_service = get_chat_service()

    kbs = kb_manager.list_knowledge_bases()
    sessions = chat_service.list_sessions()

    return {
        "knowledge_bases": len(kbs),
        "total_documents": sum(kb.document_count for kb in kbs),
        "total_chunks": sum(kb.chunk_count for kb in kbs),
        "chat_sessions": len(sessions),
        "total_messages": sum(len(s.messages) for s in sessions),
    }


# ==================== 运行服务 ====================


def main():
    """启动服务"""
    import uvicorn

    print("\n" + "=" * 50)
    print("🏢 企业级 AI 平台 API 服务")
    print("=" * 50)

    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
    )


if __name__ == "__main__":
    main()
