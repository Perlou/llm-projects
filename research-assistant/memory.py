"""
记忆管理模块
管理 Agent 的对话历史和工作记忆
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MemoryEntry:
    """记忆条目"""

    role: str  # "human", "ai", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationMemory:
    """对话记忆"""

    def __init__(self, max_entries: int = 50):
        self.entries: List[MemoryEntry] = []
        self.max_entries = max_entries

    def add(self, role: str, content: str, metadata: Dict = None):
        """添加记忆"""
        entry = MemoryEntry(role=role, content=content, metadata=metadata or {})
        self.entries.append(entry)

        # 保持记忆在限制内
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries :]

    def get_history(self, n: int = None) -> List[Dict]:
        """获取历史记录"""
        entries = self.entries[-n:] if n else self.entries
        return [{"role": e.role, "content": e.content} for e in entries]

    def get_context_string(self, n: int = 10) -> str:
        """获取上下文字符串"""
        recent = self.entries[-n:]
        lines = []
        for entry in recent:
            prefix = {"human": "用户", "ai": "助手", "system": "系统"}.get(
                entry.role, entry.role
            )
            lines.append(f"{prefix}: {entry.content}")
        return "\n".join(lines)

    def clear(self):
        """清空记忆"""
        self.entries = []

    def search(self, keyword: str) -> List[MemoryEntry]:
        """搜索记忆"""
        return [e for e in self.entries if keyword.lower() in e.content.lower()]


class WorkingMemory:
    """工作记忆 - 存储当前任务的临时信息"""

    def __init__(self):
        self.task: Optional[str] = None
        self.findings: List[str] = []
        self.sources: List[str] = []
        self.current_step: int = 0

    def set_task(self, task: str):
        """设置当前任务"""
        self.task = task
        self.findings = []
        self.sources = []
        self.current_step = 0

    def add_finding(self, finding: str):
        """添加发现"""
        self.findings.append(finding)

    def add_source(self, source: str):
        """添加来源"""
        if source not in self.sources:
            self.sources.append(source)

    def increment_step(self):
        """增加步骤计数"""
        self.current_step += 1

    def get_summary(self) -> str:
        """获取摘要"""
        if not self.task:
            return "暂无进行中的任务"

        return f"""当前任务: {self.task}
已完成步骤: {self.current_step}
收集发现: {len(self.findings)} 条
信息来源: {len(self.sources)} 个"""

    def reset(self):
        """重置工作记忆"""
        self.task = None
        self.findings = []
        self.sources = []
        self.current_step = 0


class AgentMemory:
    """Agent 记忆系统"""

    def __init__(self):
        self.conversation = ConversationMemory()
        self.working = WorkingMemory()

    def start_task(self, task: str):
        """开始新任务"""
        self.working.set_task(task)
        self.conversation.add("human", task)

    def record_thought(self, thought: str):
        """记录思考"""
        self.conversation.add("ai", f"[思考] {thought}")

    def record_action(self, action: str, input_text: str):
        """记录行动"""
        self.conversation.add("ai", f"[行动] {action}({input_text})")
        self.working.increment_step()

    def record_observation(self, observation: str):
        """记录观察"""
        self.conversation.add("system", f"[观察] {observation[:500]}")

    def record_finding(self, finding: str, source: str = None):
        """记录发现"""
        self.working.add_finding(finding)
        if source:
            self.working.add_source(source)

    def get_context(self) -> str:
        """获取当前上下文"""
        return f"""{self.working.get_summary()}

最近对话:
{self.conversation.get_context_string(5)}"""

    def reset(self):
        """重置记忆"""
        self.working.reset()
