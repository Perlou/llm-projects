"""
聊天引擎模块
核心对话处理逻辑
"""

from typing import Generator, Optional
import google.generativeai as genai

from config import config
from memory import ConversationMemory
from prompts import get_system_prompt
from utils import count_messages_tokens


class ChatEngine:
    """聊天引擎"""

    def __init__(self, mode: str = "通用助手"):
        # 配置 Gemini API
        genai.configure(api_key=config.google_api_key)

        # 创建模型实例
        self.model = genai.GenerativeModel(
            model_name=config.model_name,
            generation_config={
                "temperature": config.temperature,
                "max_output_tokens": config.max_tokens,
            },
        )

        self.memory = ConversationMemory()
        self.mode = mode
        self._set_mode(mode)

    def _set_mode(self, mode: str):
        """设置对话模式"""
        self.mode = mode
        system_prompt = get_system_prompt(mode)
        self.memory.set_system(system_prompt)

    def change_mode(self, mode: str):
        """切换模式（保留历史）"""
        self._set_mode(mode)

    def _messages_to_gemini_format(self, messages: list) -> tuple:
        """将消息转换为Gemini格式

        Returns:
            (system_instruction, history, current_message)
        """
        system_instruction = None
        history = []
        current_message = None

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = content
            elif role == "user":
                current_message = content
            elif role == "assistant":
                # Gemini的历史格式：{"role": "user"/"model", "parts": [text]}
                if current_message:  # 只有当有user消息时才添加到历史
                    history.append({"role": "user", "parts": [current_message]})
                    history.append({"role": "model", "parts": [content]})
                    current_message = None

        return system_instruction, history, current_message

    def chat(self, message: str) -> str:
        """同步聊天"""
        # 添加用户消息
        self.memory.add_user(message)

        # 构建消息
        messages = self.memory.get_messages()
        system_instruction, history, current_message = self._messages_to_gemini_format(
            messages
        )

        # 创建聊天会话
        chat = self.model.start_chat(history=history)

        # 调用 API
        response = chat.send_message(current_message or message)

        # 提取回复
        assistant_message = response.text

        # 添加助手消息
        self.memory.add_assistant(assistant_message)

        return assistant_message

    def stream_chat(self, message: str) -> Generator[str, None, None]:
        """流式聊天"""
        # 添加用户消息
        self.memory.add_user(message)

        # 构建消息
        messages = self.memory.get_messages()
        system_instruction, history, current_message = self._messages_to_gemini_format(
            messages
        )

        # 创建聊天会话
        chat = self.model.start_chat(history=history)

        # 流式调用 API
        response = chat.send_message(current_message or message, stream=True)

        # 收集完整回复
        full_response = ""

        for chunk in response:
            if chunk.text:
                content = chunk.text
                full_response += content
                yield content

        # 添加助手消息
        self.memory.add_assistant(full_response)

    def get_token_count(self) -> int:
        """获取当前对话的 token 数量"""
        messages = self.memory.get_messages()
        return count_messages_tokens(messages)

    def get_history(self) -> list:
        """获取 Gradio 格式的历史"""
        return self.memory.get_history()

    def clear_history(self):
        """清空对话历史"""
        self.memory.clear()

    def export_history(self) -> str:
        """导出对话历史"""
        return self.memory.export()


def create_engine(mode: str = "通用助手") -> ChatEngine:
    """创建聊天引擎实例"""
    return ChatEngine(mode=mode)
