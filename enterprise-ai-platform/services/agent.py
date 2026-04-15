"""
Agent 服务
==========

工作流自动化 Agent，支持工具调用和任务编排。
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from langchain.agents import create_agent
from langchain.tools import BaseTool, tool
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from config import config
from services.llm_provider import get_llm
from services.knowledge_base import get_kb_manager


@dataclass
class AgentStep:
    """Agent 执行步骤"""

    thought: str
    action: str
    action_input: Any
    observation: str


@dataclass
class AgentResult:
    """Agent 执行结果"""

    output: str
    steps: List[AgentStep] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


# ==================== 内置工具 ====================


@tool
def search_knowledge_base(query: str, kb_id: str = None) -> str:
    """在知识库中搜索信息。

    Args:
        query: 搜索查询
        kb_id: 知识库 ID（可选，不指定则使用第一个知识库）
    """
    try:
        manager = get_kb_manager()
        kbs = manager.list_knowledge_bases()

        if not kbs:
            return "没有可用的知识库"

        if kb_id:
            kb = manager.get_knowledge_base(kb_id)
            if not kb:
                return f"知识库不存在: {kb_id}"
        else:
            kb = kbs[0]

        result = manager.query(kb.id, query)
        return f"回答: {result.answer}\n\n来源: {', '.join([s['filename'] for s in result.sources])}"

    except Exception as e:
        return f"搜索失败: {str(e)}"


@tool
def list_knowledge_bases() -> str:
    """列出所有可用的知识库。"""
    try:
        manager = get_kb_manager()
        kbs = manager.list_knowledge_bases()

        if not kbs:
            return "没有可用的知识库"

        result = "可用的知识库:\n"
        for kb in kbs:
            result += f"- {kb.name} (ID: {kb.id}, 文档数: {kb.document_count})\n"
        return result

    except Exception as e:
        return f"获取知识库列表失败: {str(e)}"


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。

    Args:
        expression: 数学表达式，如 "2 + 2" 或 "100 * 0.15"
    """
    try:
        # 安全计算
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "表达式包含不允许的字符"

        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def get_current_time() -> str:
    """获取当前日期和时间。"""
    from datetime import datetime

    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"


@tool
def summarize_text(text: str) -> str:
    """对文本进行摘要。

    Args:
        text: 需要摘要的文本
    """
    try:
        llm = get_llm(temperature=0.3)
        prompt = ChatPromptTemplate.from_template(
            "请对以下文本进行简洁的摘要，保留关键信息：\n\n{text}\n\n摘要："
        )
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"text": text})
    except Exception as e:
        return f"摘要失败: {str(e)}"


# ==================== Agent 实现 ====================


class WorkflowAgent:
    """工作流 Agent"""

    SYSTEM_PROMPT = """你是一个智能工作流助手。

你可以在需要时调用工具完成任务，优先遵循以下原则：
1. 需要知识库信息时使用知识库相关工具
2. 需要数学计算时使用 calculate
3. 需要当前时间时使用 get_current_time
4. 需要对给定文本做摘要时使用 summarize_text
5. 如果任务不需要工具，直接回答

回答要准确、简洁。"""

    def __init__(self, tools: List[BaseTool] = None):
        self.tools = tools or self._get_default_tools()
        self.llm = get_llm(temperature=0.3)
        self.agent = self._create_agent()

    def _get_default_tools(self) -> List[BaseTool]:
        """获取默认工具集"""
        return [
            search_knowledge_base,
            list_knowledge_bases,
            calculate,
            get_current_time,
            summarize_text,
        ]

    def _create_agent(self):
        """创建 Agent"""
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.SYSTEM_PROMPT,
        )

    def _stringify_content(self, content: Any) -> str:
        """将消息内容规整为字符串。"""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if text:
                        parts.append(str(text))
            return "\n".join(parts).strip()
        if content is None:
            return ""
        return str(content)

    def _extract_output(self, result: Dict[str, Any]) -> str:
        """从 Agent 结果中提取最终输出。"""
        messages = result.get("messages", [])
        for message in reversed(messages):
            content = self._stringify_content(getattr(message, "content", None))
            if content:
                return content
        return ""

    def _extract_steps(self, result: Dict[str, Any]) -> List[AgentStep]:
        """从消息序列中提取工具调用步骤。"""
        steps: List[AgentStep] = []
        pending_steps: Dict[str, AgentStep] = {}

        for message in result.get("messages", []):
            if isinstance(message, AIMessage):
                for tool_call in getattr(message, "tool_calls", []):
                    tool_call_id = tool_call.get("id", "")
                    step = AgentStep(
                        thought="",
                        action=tool_call.get("name", ""),
                        action_input=json.dumps(
                            tool_call.get("args", {}),
                            ensure_ascii=False,
                        ),
                        observation="",
                    )
                    steps.append(step)
                    if tool_call_id:
                        pending_steps[tool_call_id] = step
            elif isinstance(message, ToolMessage):
                observation = self._stringify_content(message.content)
                tool_call_id = getattr(message, "tool_call_id", "")
                if tool_call_id and tool_call_id in pending_steps:
                    pending_steps[tool_call_id].observation = observation[:500]
                elif steps:
                    steps[-1].observation = observation[:500]

        return steps

    def run(self, task: str) -> AgentResult:
        """执行任务"""
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": task}]}
            )
            steps = self._extract_steps(result)

            return AgentResult(
                output=self._extract_output(result),
                steps=steps,
                success=True,
            )

        except Exception as e:
            return AgentResult(
                output="",
                success=False,
                error=str(e),
            )


# 全局实例
_agent: Optional[WorkflowAgent] = None


def get_agent() -> WorkflowAgent:
    """获取 Agent 实例"""
    global _agent
    if _agent is None:
        _agent = WorkflowAgent()
    return _agent
