"""
Claude 模型封装
"""

import time
from typing import AsyncGenerator
from anthropic import AsyncAnthropic
from .base import BaseModel, ChatMessage, ChatResponse, StreamChunk


class ClaudeModel(BaseModel):
    """Claude 模型"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.client = AsyncAnthropic(api_key=api_key)

    async def chat(
        self,
        messages: list[ChatMessage],
        stream: bool = False,
    ) -> ChatResponse:
        start_time = time.time()

        try:
            system_content = ""
            api_messages = []

            for m in messages:
                if m.role == "system":
                    system_content = m.content
                else:
                    api_messages.append({"role": m.role, "content": m.content})

            response = await self.client.messages.create(
                model=self.model_id,
                max_tokens=self.max_tokens,
                system=system_content if system_content else None,
                messages=api_messages,
            )

            total_time = time.time() - start_time

            return ChatResponse(
                content=response.content[0].text,
                model=self.name,
                provider=self.provider,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                first_token_time=total_time,
                total_time=total_time,
                cost=self.calculate_cost(
                    response.usage.input_tokens, response.usage.output_tokens
                ),
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
        system_content = ""
        api_messages = []

        for m in messages:
            if m.role == "system":
                system_content = m.content
            else:
                api_messages.append({"role": m.role, "content": m.content})

        is_first = True
        async with self.client.messages.stream(
            model=self.model_id,
            max_tokens=self.max_tokens,
            system=system_content if system_content else None,
            messages=api_messages,
        ) as stream:
            async for text in stream.text_stream:
                yield StreamChunk(
                    content=text,
                    is_first=is_first,
                    is_last=False,
                )
                is_first = False

        yield StreamChunk(content="", is_first=False, is_last=True)

    async def is_available(self) -> bool:
        """检查模型是否可用"""
        try:
            # Claude 没有 models.list API，尝试简单请求
            await self.client.messages.create(
                model=self.model_id,
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
            return True
        except Exception:
            return False
