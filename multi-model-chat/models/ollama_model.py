"""
Ollama 模型封装（本地模型）
"""

import time
from typing import AsyncGenerator
from openai import AsyncOpenAI
from .base import BaseModel, ChatMessage, ChatResponse, StreamChunk


class OllamaModel(BaseModel):
    """Ollama 本地模型（使用 OpenAI 兼容接口）"""

    def __init__(self, host: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self.client = AsyncOpenAI(
            base_url=f"{host}/v1",
            api_key="ollama",  # Ollama 不需要真实 API key
        )
        self.host = host

    async def chat(
        self,
        messages: list[ChatMessage],
        stream: bool = False,
    ) -> ChatResponse:
        """发送聊天请求"""
        start_time = time.time()

        try:
            # 转换消息格式
            api_messages = [{"role": m.role, "content": m.content} for m in messages]

            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=api_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            total_time = time.time() - start_time

            # Ollama 可能不返回 token 数
            input_tokens = 0
            output_tokens = 0
            if response.usage:
                input_tokens = response.usage.prompt_tokens or 0
                output_tokens = response.usage.completion_tokens or 0

            return ChatResponse(
                content=response.choices[0].message.content,
                model=self.name,
                provider=self.provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                first_token_time=total_time,
                total_time=total_time,
                cost=0.0,  # 本地模型免费
            )

        except Exception as e:
            return ChatResponse(
                content="",
                model=self.name,
                provider=self.provider,
                total_time=time.time() - start_time,
                error=str(e),
            )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
    ) -> AsyncGenerator[StreamChunk, None]:
        """流式聊天请求"""
        api_messages = [{"role": m.role, "content": m.content} for m in messages]

        stream = await self.client.chat.completions.create(
            model=self.model_id,
            messages=api_messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        )

        is_first = True
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield StreamChunk(
                    content=chunk.choices[0].delta.content,
                    is_first=is_first,
                    is_last=False,
                )
                is_first = False

            if chunk.choices[0].finish_reason:
                yield StreamChunk(
                    content="",
                    is_first=False,
                    is_last=True,
                )

    async def is_available(self) -> bool:
        """检查模型是否可用"""
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
