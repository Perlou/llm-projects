"""
LLM 提供者
==========

统一的 LLM 接口，支持 Gemini 和 Ollama。
"""

from typing import Optional, AsyncIterator, Iterator
from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from config import config


class LLMProvider(ABC):
    """LLM 提供者基类"""

    @abstractmethod
    def get_llm(self, temperature: float = 0.7) -> BaseChatModel:
        """获取 LLM 实例"""
        pass

    @abstractmethod
    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """同步对话"""
        pass

    @abstractmethod
    async def achat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """异步对话"""
        pass


class GeminiProvider(LLMProvider):
    """Gemini 提供者"""

    def __init__(self):
        self.api_key = config.google_api_key
        self.model_name = config.gemini_model

    def get_llm(self, temperature: float = 0.7) -> BaseChatModel:
        """获取 Gemini LLM"""
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=temperature,
        )

    def get_embeddings(self):
        """获取 Embedding 模型"""
        return GoogleGenerativeAIEmbeddings(
            model=config.embedding_model,
            google_api_key=self.api_key,
        )

    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """同步对话"""
        llm = self.get_llm()
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        response = llm.invoke(messages)
        return response.content

    async def achat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """异步对话"""
        llm = self.get_llm()
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        response = await llm.ainvoke(messages)
        return response.content

    def stream(
        self, message: str, system_prompt: Optional[str] = None
    ) -> Iterator[str]:
        """流式对话"""
        llm = self.get_llm()
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        for chunk in llm.stream(messages):
            if chunk.content:
                yield chunk.content

    async def astream(
        self, message: str, system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """异步流式对话"""
        llm = self.get_llm()
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content


class OllamaProvider(LLMProvider):
    """Ollama 本地模型提供者"""

    def __init__(self):
        self.base_url = config.ollama_base_url
        self.model_name = config.ollama_model

    def get_llm(self, temperature: float = 0.7) -> BaseChatModel:
        """获取 Ollama LLM"""
        return ChatOllama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=temperature,
        )

    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """同步对话"""
        llm = self.get_llm()
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        response = llm.invoke(messages)
        return response.content

    async def achat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """异步对话"""
        llm = self.get_llm()
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        response = await llm.ainvoke(messages)
        return response.content

    def stream(
        self, message: str, system_prompt: Optional[str] = None
    ) -> Iterator[str]:
        """流式对话"""
        llm = self.get_llm()
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        for chunk in llm.stream(messages):
            if chunk.content:
                yield chunk.content

    async def astream(
        self, message: str, system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """异步流式对话"""
        llm = self.get_llm()
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content


def get_provider() -> LLMProvider:
    """根据配置获取 LLM 提供者"""
    if config.llm_provider == "gemini":
        return GeminiProvider()
    else:
        return OllamaProvider()


def get_llm(temperature: float = 0.7) -> BaseChatModel:
    """获取 LLM 实例（便捷函数）"""
    return get_provider().get_llm(temperature)


def get_embeddings():
    """获取 Embedding 模型"""
    # 目前只有 Gemini 支持 embedding
    return GoogleGenerativeAIEmbeddings(
        model=config.embedding_model,
        google_api_key=config.google_api_key,
    )
