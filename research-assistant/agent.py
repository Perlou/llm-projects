"""
ReAct Agent 实现
思考-行动-观察循环的 Agent
"""

from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool

from config import config
from memory import AgentMemory
from tools.search import SearchTool
from tools.reader import ReaderTool
from tools.writer import WriterTool
from tools.note import NoteTool


class ResearchAgent:
    """研究助手 Agent"""

    SYSTEM_PROMPT = """你是一位专业的研究助手，擅长搜索、阅读和整理信息。

你可以使用以下工具来完成研究任务：

{tools}

工具名称列表: {tool_names}

执行研究任务时，请遵循以下步骤：
1. 首先理解用户的研究需求
2. 使用 search 工具搜索相关信息
3. 使用 read_url 工具深入阅读重要内容
4. 使用 take_note 工具记录关键发现
5. 收集足够信息后，使用 write_report 生成研究报告

使用以下格式思考和行动：

Question: 需要回答的研究问题
Thought: 思考下一步应该做什么
Action: 要使用的工具名称，必须是 [{tool_names}] 中的一个
Action Input: 工具的输入
Observation: 工具返回的结果
... (Thought/Action/Action Input/Observation 可以重复多次)
Thought: 我已经完成了研究任务
Final Answer: 对研究任务的最终总结

注意：
- 每次只能使用一个工具
- 仔细阅读每个工具的描述，正确使用
- 记得用 take_note 记录重要发现
- 确保最终给出完整的答案

开始！

Question: {input}
Thought: {agent_scratchpad}"""

    def __init__(self):
        self.memory = AgentMemory()
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent()

    def _create_tools(self) -> List[BaseTool]:
        """创建工具集"""
        tools = [
            SearchTool(),
            ReaderTool(),
            WriterTool(),
        ]
        tools.extend(NoteTool.get_tools())
        return tools

    def _create_agent(self) -> AgentExecutor:
        """创建 Agent"""
        llm = ChatGoogleGenerativeAI(
            model=config.llm_model,
            google_api_key=config.google_api_key,
            temperature=0.3,
        )

        prompt = PromptTemplate.from_template(self.SYSTEM_PROMPT)

        agent = create_react_agent(
            llm=llm,
            tools=self.tools,
            prompt=prompt,
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=config.verbose,
            max_iterations=config.max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def run(self, task: str) -> str:
        """执行研究任务"""
        self.memory.start_task(task)

        try:
            result = self.agent_executor.invoke({"input": task})

            # 提取输出
            output = result.get("output", "任务完成")

            return output

        except Exception as e:
            return f"执行任务时出错: {str(e)}"

    def get_steps(self, result: dict) -> List[dict]:
        """获取中间步骤"""
        steps = []
        for action, observation in result.get("intermediate_steps", []):
            steps.append(
                {
                    "thought": getattr(action, "log", ""),
                    "action": action.tool,
                    "action_input": action.tool_input,
                    "observation": observation[:500] if observation else "",
                }
            )
        return steps

    def clear_notes(self):
        """清空笔记"""
        NoteTool.get_manager().clear_notes()

    def reset(self):
        """重置 Agent 状态"""
        self.memory.reset()
        self.clear_notes()


def create_agent() -> ResearchAgent:
    """创建研究助手实例"""
    return ResearchAgent()
