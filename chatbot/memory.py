"""
对话记忆模块
管理多轮对话历史
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

from config import config


@dataclass
class Message:
    """对话消息"""

    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationMemory:
    """对话记忆"""

    def __init__(self, max_history: int = None):
        self.max_history = max_history or config.max_history
        self.messages: List[Message] = []
        self.system_message: Optional[str] = None

    def set_system(self, content: str):
        """设置系统消息"""
        self.system_message = content

    def add_user(self, content: str):
        """添加用户消息"""
        self.messages.append(Message(role="user", content=content))
        self._trim()

    def add_assistant(self, content: str):
        """添加助手消息"""
        self.messages.append(Message(role="assistant", content=content))
        self._trim()

    def _trim(self):
        """保持历史在限制内"""
        # 保留最近的消息对（用户+助手各算一条）
        if len(self.messages) > self.max_history * 2:
            self.messages = self.messages[-self.max_history * 2 :]

    def get_messages(self) -> List[Dict]:
        """获取 OpenAI 格式的消息列表"""
        messages = []

        # 添加系统消息
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})

        # 添加历史消息
        for msg in self.messages:
            messages.append({"role": msg.role, "content": msg.content})

        return messages

    def get_history(self) -> List[tuple]:
        history = []
        i = 0
        while i < len(self.messages):
            if self.messages[i].role == "user":
                user_msg = self.messages[i].content
                assistant_msg = ""
                if (
                    i + 1 < len(self.messages)
                    and self.messages[i + 1].role == "assistant"
                ):
                    assistant_msg = self.messages[i + 1].content
                    i += 1
                history.append((user_msg, assistant_msg))

            i += 1
        return history

    def clear(self):
        """清空历史"""
        self.messages = []

    def get_message_count(self) -> int:
        """获取消息数量"""
        return len(self.messages)

    def export(self) -> str:
        """导出对话记录"""
        lines = []
        for msg in self.messages:
            role = "👤 用户" if msg.role == "user" else "🤖 助手"
            lines.append(f"{role}:\n{msg.content}\n")
        return "\n".join(lines)
