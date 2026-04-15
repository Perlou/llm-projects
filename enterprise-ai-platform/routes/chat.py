"""
对话 API 路由
=============

对话相关的 REST API 端点。
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from services.chat import get_chat_service


router = APIRouter(prefix="/api/chat", tags=["对话"])


# ==================== 数据模型 ====================


class ChatRequest(BaseModel):
    """对话请求"""

    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话 ID")
    system_prompt: Optional[str] = Field(None, description="系统提示词")


class ChatResponse(BaseModel):
    """对话响应"""

    response: str
    session_id: str


class SessionInfo(BaseModel):
    """会话信息"""

    id: str
    title: str
    message_count: int
    created_at: str


class MessageInfo(BaseModel):
    """消息信息"""

    role: str
    content: str
    timestamp: str


# ==================== API 端点 ====================


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    发送消息并获取回复

    - **message**: 用户消息
    - **session_id**: 可选的会话 ID，不提供则创建新会话
    - **system_prompt**: 可选的系统提示词
    """
    try:
        service = get_chat_service()
        response = service.chat(
            message=request.message,
            session_id=request.session_id,
            system_prompt=request.system_prompt,
        )

        # 获取当前会话 ID
        session = service.get_current_session()
        session_id = session.id if session else ""

        return ChatResponse(response=response, session_id=session_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    流式对话

    返回 SSE (Server-Sent Events) 格式的流式响应
    """
    try:
        service = get_chat_service()

        async def generate():
            async for chunk in service.astream(
                message=request.message,
                session_id=request.session_id,
                system_prompt=request.system_prompt,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """获取所有会话列表"""
    service = get_chat_service()
    sessions = service.list_sessions()

    return [
        SessionInfo(
            id=s.id,
            title=s.title,
            message_count=len(s.messages),
            created_at=s.created_at,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages", response_model=List[MessageInfo])
async def get_session_messages(session_id: str):
    """获取会话的消息历史"""
    service = get_chat_service()
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return [
        MessageInfo(
            role=m.role,
            content=m.content,
            timestamp=m.timestamp,
        )
        for m in session.messages
    ]


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    service = get_chat_service()
    service.clear_session(session_id)
    return {"success": True}


@router.post("/sessions")
async def create_session(system_prompt: Optional[str] = None):
    """创建新会话"""
    service = get_chat_service()
    session = service.create_session(system_prompt)
    return SessionInfo(
        id=session.id,
        title=session.title,
        message_count=0,
        created_at=session.created_at,
    )
