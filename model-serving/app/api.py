"""
API 路由模块
"""

import uuid
import time
import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from app.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    Usage,
    Message,
    HealthResponse,
    StatsResponse,
)
from app.engine import get_engine
from app.config import settings


router = APIRouter()

# 统计信息
_stats = {
    "total_requests": 0,
    "active_requests": 0,
    "total_latency_ms": 0,
    "start_time": time.time(),
}


@router.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """聊天补全接口 (OpenAI 兼容)"""
    _stats["total_requests"] += 1
    _stats["active_requests"] += 1
    start_time = time.time()

    try:
        engine = get_engine()

        if request.stream:
            return EventSourceResponse(
                stream_response(request, engine),
                media_type="text/event-stream",
            )

        # 非流式响应
        response_text = engine.generate(
            messages=request.messages,
            max_tokens=request.max_tokens or settings.max_new_tokens,
            temperature=request.temperature or settings.temperature,
            top_p=request.top_p or settings.top_p,
        )

        # 计算 token
        prompt_text = "\n".join([m.content for m in request.messages])
        prompt_tokens = engine.count_tokens(prompt_text)
        completion_tokens = engine.count_tokens(response_text)

        response = ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(role="assistant", content=response_text),
                    finish_reason="stop",
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )

        latency = (time.time() - start_time) * 1000
        _stats["total_latency_ms"] += latency

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        _stats["active_requests"] -= 1


async def stream_response(
    request: ChatCompletionRequest,
    engine,
) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    request_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

    try:
        for chunk in engine.stream_generate(
            messages=request.messages,
            max_tokens=request.max_tokens or settings.max_new_tokens,
            temperature=request.temperature or settings.temperature,
            top_p=request.top_p or settings.top_p,
        ):
            response = ChatCompletionStreamResponse(
                id=request_id,
                model=request.model,
                choices=[
                    ChatCompletionStreamChoice(
                        index=0,
                        delta={"content": chunk},
                        finish_reason=None,
                    )
                ],
            )
            yield json.dumps(response.model_dump())

        # 发送结束标记
        final_response = ChatCompletionStreamResponse(
            id=request_id,
            model=request.model,
            choices=[
                ChatCompletionStreamChoice(
                    index=0,
                    delta={},
                    finish_reason="stop",
                )
            ],
        )
        yield json.dumps(final_response.model_dump())
        yield "[DONE]"

    except Exception as e:
        yield json.dumps({"error": str(e)})


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    try:
        engine = get_engine()
        return HealthResponse(
            status="healthy",
            model=settings.model_name,
            engine=settings.inference_engine,
        )
    except Exception as e:
        return HealthResponse(
            status=f"unhealthy: {str(e)}",
            model=settings.model_name,
            engine=settings.inference_engine,
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取统计信息"""
    total = _stats["total_requests"]
    avg_latency = _stats["total_latency_ms"] / total if total > 0 else 0

    return StatsResponse(
        total_requests=total,
        active_requests=_stats["active_requests"],
        avg_latency_ms=avg_latency,
        model=settings.model_name,
        uptime_seconds=time.time() - _stats["start_time"],
    )


@router.get("/v1/models")
async def list_models():
    """模型列表 (OpenAI 兼容)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "default",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local",
            }
        ],
    }
