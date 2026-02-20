"""
Gemini 模型封装
"""

import time
from typing import AsyncGenerator
import google.generativeai as genai
from .base import BaseModel, ChatMessage, ChatResponse, StreamChunk


class GeminiModel(BaseModel):
    """Gemini 模型"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        genai.configure(api_key=api_key)

        # 分离 system 指令
        self.system_instruction = None
        self._model = None

    def _get_model(self, system_instruction: str = None):
        """获取模型实例"""
        return genai.GenerativeModel(
            self.model_id,
            system_instruction=system_instruction,
        )

    async def chat(
        self,
        messages: list[ChatMessage],
        stream: bool = False,
    ) -> ChatResponse:
        """发送聊天请求"""
        start_time = time.time()

        try:
            # 分离 system 消息
            system_content = None
            chat_messages = []

            for m in messages:
                if m.role == "system":
                    system_content = m.content
                else:
                    chat_messages.append(m)

            model = self._get_model(system_content)

            # 构建对话历史
            history = []
            for m in chat_messages[:-1]:  # 除了最后一条
                role = "user" if m.role == "user" else "model"
                history.append({"role": role, "parts": [m.content]})

            # 开始对话
            chat = model.start_chat(history=history)

            # 发送最后一条消息
            last_message = chat_messages[-1].content if chat_messages else ""
            response = await chat.send_message_async(last_message)

            total_time = time.time() - start_time

            # Gemini 的 token 统计
            input_tokens = 0
            output_tokens = 0
            if hasattr(response, "usage_metadata"):
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count

            return ChatResponse(
                content=response.text,
                model=self.name,
                provider=self.provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                first_token_time=total_time,
                total_time=total_time,
                cost=self.calculate_cost(input_tokens, output_tokens),
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
        # 分离 system 消息
        system_content = None
        chat_messages = []

        for m in messages:
            if m.role == "system":
                system_content = m.content
            else:
                chat_messages.append(m)

        model = self._get_model(system_content)

        # 构建对话历史
        history = []
        for m in chat_messages[:-1]:
            role = "user" if m.role == "user" else "model"
            history.append({"role": role, "parts": [m.content]})

        chat = model.start_chat(history=history)
        last_message = chat_messages[-1].content if chat_messages else ""

        is_first = True
        response = await chat.send_message_async(last_message, stream=True)

        async for chunk in response:
            if chunk.text:
                yield StreamChunk(
                    content=chunk.text,
                    is_first=is_first,
                    is_last=False,
                )
                is_first = False

        yield StreamChunk(content="", is_first=False, is_last=True)

    async def is_available(self) -> bool:
        """检查模型是否可用"""
        try:
            model = self._get_model()
            await model.generate_content_async("hi")
            return True
        except Exception:
            return False
