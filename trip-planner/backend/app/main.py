"""FastAPI 入口"""
from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import get_service
from .config import get_settings
from .schemas import TripPlanResponse, TripRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("trip-planner")

settings = get_settings()

app = FastAPI(
    title="ClearAgent 旅行规划助手",
    version="0.1.0",
    description="基于 ClearAgent 框架（MCP + ReActAgent + 结构化输出）的旅行规划 demo",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup() -> None:
    """启动时只校验配置；Agent 在首请求时懒加载。

    为什么不在 startup 里预热？
    ------------------------------
    ``MCPClient.register_to()`` 内部走 ``asyncio.run(...)``，
    而 startup hook 已经在运行的 event loop 里，
    在 running loop 里再 ``asyncio.run`` 会抛
    ``RuntimeError: asyncio.run() cannot be called from a running event loop``。
    sync 的 POST handler 跑在 FastAPI 的 threadpool 工作线程里，
    那个线程没有 loop，``asyncio.run`` 可以正常工作。
    """
    logger.info("启动中：校验配置 ...")
    try:
        settings.assert_ready()
        logger.info(
            "✅ 配置 OK，监听 %s:%d。Agent 将在首次请求 /api/trip/plan 时懒加载（首次约 5~30s）。",
            settings.app_host,
            settings.app_port,
        )
        # 在后台线程预热，避免首请求等待，又不阻塞当前 startup loop
        asyncio.get_event_loop().run_in_executor(None, _preload_agent)
    except Exception as exc:  # noqa: BLE001
        # 不抛 —— 让 / 与 /health 仍可访问，便于排查
        logger.error("❌ 启动配置校验失败：%s", exc)


def _preload_agent() -> None:
    """后台线程里预热 Agent —— 此线程无 event loop，asyncio.run 可正常工作"""
    try:
        logger.info("🔥 后台线程预热 Agent（uvx amap-mcp-server + 注册工具）...")
        get_service()
        logger.info("✅ Agent 已预热完成，下一次请求将秒级响应")
    except Exception as exc:  # noqa: BLE001
        logger.error("⚠️ Agent 预热失败（不影响后续按需懒加载）：%s", exc)


@app.get("/")
def root() -> dict:
    return {
        "name": "clear-agent-trip-planner",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/trip/plan", response_model=TripPlanResponse)
def plan(request: TripRequest) -> TripPlanResponse:
    """生成旅行计划

    handler 必须用 ``def``（非 ``async def``）—— 否则会运行在主 loop 里，
    内部 ``MCPClient`` 的 ``asyncio.run`` 会冲突。
    sync handler 由 FastAPI 自动放进 threadpool，工作线程没有 loop，OK。
    """
    if request.travel_days <= 0:
        raise HTTPException(status_code=400, detail="travel_days 必须为正整数")
    try:
        service = get_service()
        trip = service.plan(request)
        return TripPlanResponse(success=True, message="ok", data=trip)
    except Exception as exc:  # noqa: BLE001
        logger.exception("规划失败：%s", exc)
        return TripPlanResponse(success=False, message=str(exc), data=None)
