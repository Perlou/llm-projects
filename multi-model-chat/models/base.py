"""
模型基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator, Optional
import time


@dataclass
class ChatMessage:
    """聊天消息"""

    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ChatResponse:
    """聊天响应"""

    content: str
    model: str
    provider: str

    # 统计信息
    input_tokens: int = 0
    output_tokens: int = 0
    first_token_time: float = 0.0  # TTFT
    total_time: float = 0.0

    # 成本（美元）
    cost: float = 0.0

    # 错误信息
    error: Optional[str] = None


@dataclass
class StreamChunk:
    """流式响应块"""

    content: str
    is_first: bool = False
    is_last: bool = False


class BaseModel(ABC):
    """模型基类"""

    def __init__(
        self,
        name: str,
        provider: str,
        model_id: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        input_price: float = 0.0,
        output_price: float = 0.0,
    ):
        self.name = name
        self.provider = provider
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.input_price = input_price
        self.output_price = output_price

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        stream: bool = False,
    ) -> ChatResponse:
        """发送聊天请求"""
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[ChatMessage],
    ) -> AsyncGenerator[StreamChunk, None]:
        """流式聊天请求"""
        pass

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算成本"""
        return (
            input_tokens * self.input_price / 1000
            + output_tokens * self.output_price / 1000
        )

    @abstractmethod
    async def is_available(self) -> bool:
        """检查模型是否可用"""
        pass
