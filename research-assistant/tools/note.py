"""
笔记管理工具
记录和管理研究笔记
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from langchain_core.tools import BaseTool
from pydantic import Field

from config import config


class NoteManager:
    """笔记管理器"""

    def __init__(self):
        self.notes_file = os.path.join(config.notes_dir, "notes.json")
        self.notes: List[Dict] = []
        self._load_notes()

    def _load_notes(self):
        """加载笔记"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    self.notes = json.load(f)
            except Exception:
                self.notes = []

    def _save_notes(self):
        """保存笔记"""
        os.makedirs(config.notes_dir, exist_ok=True)
        with open(self.notes_file, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def add_note(self, title: str, content: str, tags: List[str] = None) -> Dict:
        """添加笔记"""
        note = {
            "id": len(self.notes) + 1,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
        }
        self.notes.append(note)
        self._save_notes()
        return note

    def list_notes(self) -> List[Dict]:
        """列出所有笔记"""
        return self.notes

    def get_note(self, note_id: int) -> Optional[Dict]:
        """获取指定笔记"""
        for note in self.notes:
            if note["id"] == note_id:
                return note
        return None

    def clear_notes(self):
        """清空笔记"""
        self.notes = []
        self._save_notes()

    def search_notes(self, keyword: str) -> List[Dict]:
        """搜索笔记"""
        results = []
        for note in self.notes:
            if (
                keyword.lower() in note["title"].lower()
                or keyword.lower() in note["content"].lower()
            ):
                results.append(note)
        return results


# 全局笔记管理器
note_manager = NoteManager()


class TakeNoteTool(BaseTool):
    """记录笔记工具"""

    name: str = "take_note"
    description: str = """记录研究笔记。
当你需要记录重要发现、观点或信息时使用此工具。
输入格式: "标题 | 内容"
例如: "RAG 核心思想 | RAG 通过检索外部知识来增强 LLM 的回答能力"
"""

    def _run(self, input_text: str) -> str:
        """记录笔记"""
        try:
            if "|" in input_text:
                parts = input_text.split("|", 1)
                title = parts[0].strip()
                content = parts[1].strip()
            else:
                title = "研究笔记"
                content = input_text.strip()

            note = note_manager.add_note(title, content)
            return f"✅ 笔记已保存 (ID: {note['id']})\n标题: {title}"

        except Exception as e:
            return f"保存笔记失败: {str(e)}"

    async def _arun(self, input_text: str) -> str:
        return self._run(input_text)


class ListNotesTool(BaseTool):
    """查看笔记列表工具"""

    name: str = "list_notes"
    description: str = """查看所有已记录的笔记。
当你需要回顾已收集的信息或准备写报告时使用此工具。
无需输入参数，直接调用即可。"""

    def _run(self, _: str = "") -> str:
        """列出笔记"""
        notes = note_manager.list_notes()

        if not notes:
            return "📒 暂无笔记"

        formatted = ["📒 笔记列表:"]
        for note in notes:
            formatted.append(
                f"\n{note['id']}. {note['title']}\n   {note['content'][:100]}..."
            )

        return "\n".join(formatted)

    async def _arun(self, _: str = "") -> str:
        return self._run()


class NoteTool:
    """笔记工具集"""

    @staticmethod
    def get_tools() -> List[BaseTool]:
        """获取所有笔记工具"""
        return [TakeNoteTool(), ListNotesTool()]

    @staticmethod
    def get_manager() -> NoteManager:
        """获取笔记管理器"""
        return note_manager
