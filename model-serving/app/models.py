"""
数据模型定义
OpenAI 兼容的请求/响应模型
"""

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import time


class Message(BaseModel):
    """聊天消息"""

    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    """聊天补全请求"""

    model: str = "default"
    messages: List[Message]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    max_tokens: Optional[int] = 512
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None


class ChatCompletionChoice(BaseModel):
    """聊天补全选项"""

    index: int
    message: Message
    finish_reason: Optional[str] = "stop"


class Usage(BaseModel):
    """Token 使用统计"""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """聊天补全响应"""

    id: str
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


class ChatCompletionStreamChoice(BaseModel):
    """流式响应选项"""

    index: int
    delta: dict
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(BaseModel):
    """流式响应"""

    id: str
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionStreamChoice]


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str
    model: str
    engine: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class StatsResponse(BaseModel):
    """统计信息响应"""

    total_requests: int
    active_requests: int
    avg_latency_ms: float
    model: str
    uptime_seconds: float
