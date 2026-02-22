"""
对话管理模块
管理多轮对话历史
"""

from typing import List, Optional
from dataclasses import dataclass, field
from langchain_core.messages import HumanMessage, AIMessage


@dataclass
class ChatMessage:
    """聊天消息"""

    role: str  # "user" or "assistant"
    content: str


@dataclass
class ChatSession:
    """聊天会话"""

    messages: List[ChatMessage] = field(default_factory=list)
    max_history: int = 10

    def add_user_message(self, content: str):
        """添加用户消息"""
        self.messages.append(ChatMessage(role="user", content=content))
        self._trim_history()

    def add_assistant_message(self, content: str):
        """添加助手消息"""
        self.messages.append(ChatMessage(role="assistant", content=content))
        self._trim_history()

    def _trim_history(self):
        """保持历史在限制内"""
        if len(self.messages) > self.max_history * 2:
            # 保留最近的对话
            self.messages = self.messages[-self.max_history * 2 :]

    def get_langchain_history(self) -> List:
        """转换为 LangChain 消息格式"""
        history = []
        for msg in self.messages:
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))
        return history

    def clear(self):
        """清空历史"""
        self.messages = []

    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        if not self.messages:
            return "新对话"
        return f"已有 {len(self.messages)} 条消息"


class ChatManager:
    """对话管理器"""

    def __init__(self):
        self.current_session: Optional[ChatSession] = None
        self._init_session()

    def _init_session(self):
        """初始化会话"""
        self.current_session = ChatSession()

    def add_exchange(self, user_message: str, assistant_message: str):
        """添加一轮对话"""
        self.current_session.add_user_message(user_message)
        self.current_session.add_assistant_message(assistant_message)

    def get_history(self) -> List:
        """获取 LangChain 格式的历史"""
        return self.current_session.get_langchain_history()

    def clear_history(self):
        """清空对话历史"""
        self._init_session()

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "message_count": len(self.current_session.messages),
            "context": self.current_session.get_context_summary(),
        }
