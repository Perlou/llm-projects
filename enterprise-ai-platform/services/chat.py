"""
对话服务
========

统一的对话接口，支持普通对话和 RAG 增强对话。
"""

from typing import List, Dict, Any, Optional, Iterator, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from config import config
from services.llm_provider import get_provider, get_llm


@dataclass
class ChatMessage:
    """对话消息"""

    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_langchain(self) -> BaseMessage:
        """转换为 LangChain 消息"""
        if self.role == "user":
            return HumanMessage(content=self.content)
        else:
            return AIMessage(content=self.content)


@dataclass
class ChatSession:
    """对话会话"""

    id: str
    title: str = "新对话"
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    system_prompt: Optional[str] = None

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """添加消息"""
        msg = ChatMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)

        # 自动生成标题
        if len(self.messages) == 1 and role == "user":
            self.title = content[:30] + ("..." if len(content) > 30 else "")

        return msg

    def get_history(self, max_turns: int = 10) -> List[BaseMessage]:
        """获取对话历史（LangChain 格式）"""
        recent = self.messages[-(max_turns * 2) :]
        return [msg.to_langchain() for msg in recent]


class ChatService:
    """对话服务"""

    DEFAULT_SYSTEM_PROMPT = """你是一个专业、友好的 AI 助手。

你的职责是：
1. 准确理解用户的问题
2. 提供有价值的回答
3. 保持对话的连贯性
4. 在不确定时坦诚告知

请用中文回答用户的问题。"""

    def __init__(self):
        self.provider = get_provider()
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session_id: Optional[str] = None

    def create_session(self, system_prompt: Optional[str] = None) -> ChatSession:
        """创建新会话"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        session = ChatSession(
            id=session_id,
            system_prompt=system_prompt or self.DEFAULT_SYSTEM_PROMPT,
        )
        self.sessions[session_id] = session
        self.current_session_id = session_id
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """获取会话"""
        return self.sessions.get(session_id)

    def get_current_session(self) -> Optional[ChatSession]:
        """获取当前会话"""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None

    def list_sessions(self) -> List[ChatSession]:
        """列出所有会话"""
        return sorted(self.sessions.values(), key=lambda x: x.created_at, reverse=True)

    def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """发送消息并获取回复"""
        # 获取或创建会话
        if session_id:
            session = self.get_session(session_id)
        else:
            session = self.get_current_session()

        if not session:
            session = self.create_session(system_prompt)

        # 添加用户消息
        session.add_message("user", message)

        # 构建消息列表
        messages = []
        prompt = session.system_prompt or self.DEFAULT_SYSTEM_PROMPT
        messages.append(SystemMessage(content=prompt))

        # 添加历史消息
        for msg in session.get_history():
            messages.append(msg)

        # 获取回复
        llm = self.provider.get_llm()
        response = llm.invoke(messages)
        answer = response.content

        # 添加助手回复
        session.add_message("assistant", answer)

        return answer

    def stream(
        self,
        message: str,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> Iterator[str]:
        """流式对话"""
        # 获取或创建会话
        if session_id:
            session = self.get_session(session_id)
        else:
            session = self.get_current_session()

        if not session:
            session = self.create_session(system_prompt)

        # 添加用户消息
        session.add_message("user", message)

        # 构建消息列表
        messages = []
        prompt = session.system_prompt or self.DEFAULT_SYSTEM_PROMPT
        messages.append(SystemMessage(content=prompt))

        for msg in session.get_history():
            messages.append(msg)

        # 流式获取回复
        llm = self.provider.get_llm()
        full_response = ""
        for chunk in llm.stream(messages):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content

        # 添加完整回复到历史
        session.add_message("assistant", full_response)

    async def astream(
        self,
        message: str,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """异步流式对话"""
        # 获取或创建会话
        if session_id:
            session = self.get_session(session_id)
        else:
            session = self.get_current_session()

        if not session:
            session = self.create_session(system_prompt)

        # 添加用户消息
        session.add_message("user", message)

        # 构建消息列表
        messages = []
        prompt = session.system_prompt or self.DEFAULT_SYSTEM_PROMPT
        messages.append(SystemMessage(content=prompt))

        for msg in session.get_history():
            messages.append(msg)

        # 流式获取回复
        llm = self.provider.get_llm()
        full_response = ""
        async for chunk in llm.astream(messages):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content

        # 添加完整回复到历史
        session.add_message("assistant", full_response)

    def clear_session(self, session_id: str):
        """清空会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                self.current_session_id = None


# 全局实例
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """获取对话服务实例"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
