"""
报告写作工具
生成研究报告
"""

import os
from datetime import datetime
from typing import List
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import Field

from config import config
from tools.note import note_manager


class WriterTool(BaseTool):
    """报告写作工具"""

    name: str = "write_report"
    description: str = """根据收集的笔记生成研究报告。
当你已经收集了足够的信息，需要整理成报告时使用此工具。
输入应该是报告的标题。"""

    def _run(self, title: str) -> str:
        """生成报告"""
        try:
            # 获取所有笔记
            notes = note_manager.list_notes()

            if not notes:
                return "没有可用的笔记，无法生成报告。请先使用 take_note 工具记录一些研究发现。"

            # 构建笔记内容
            notes_content = "\n\n".join(
                [f"### {note['title']}\n{note['content']}" for note in notes]
            )

            # 使用 LLM 生成报告
            llm = ChatGoogleGenerativeAI(
                model=config.llm_model,
                google_api_key=config.google_api_key,
                temperature=0.7,
            )

            prompt = f"""你是一位专业的研究报告撰写专家。请根据以下研究笔记，撰写一份结构清晰、内容丰富的研究报告。

报告标题: {title}

研究笔记:
{notes_content}

请按以下格式撰写报告:

# {title}

## 摘要
[简要概述研究发现]

## 背景介绍
[说明研究背景和重要性]

## 主要发现
[详细阐述关键发现和观点]

## 结论与建议
[总结主要结论，提出建议]

## 参考资料
[列出主要信息来源]

请确保报告专业、客观，并正确引用笔记中的信息。"""

            response = llm.invoke(prompt)
            report_content = response.content

            # 保存报告
            filename = self._save_report(title, report_content)

            return (
                f"✅ 报告已生成！\n\n保存位置: {filename}\n\n{report_content[:500]}..."
            )

        except Exception as e:
            return f"生成报告失败: {str(e)}"

    def _save_report(self, title: str, content: str) -> str:
        """保存报告到文件"""
        os.makedirs(config.reports_dir, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
        filename = f"{safe_title}_{timestamp}.md"
        filepath = os.path.join(config.reports_dir, filename)

        # 添加元数据
        metadata = f"""---
title: {title}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(metadata + content)

        return filepath

    async def _arun(self, title: str) -> str:
        return self._run(title)


def create_writer_tool() -> WriterTool:
    """创建写作工具实例"""
    return WriterTool()
