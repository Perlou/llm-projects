"""
文档处理模块
============

文档解析、摘要和信息提取功能。
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from services.llm_provider import get_llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


@dataclass
class DocumentInfo:
    """文档信息"""

    filename: str
    content: str
    page_count: int = 1
    word_count: int = 0


@dataclass
class DocumentSummary:
    """文档摘要"""

    title: str
    summary: str
    key_points: List[str]
    keywords: List[str]


@dataclass
class ExtractedInfo:
    """提取的信息"""

    entities: Dict[str, List[str]]  # 实体类型 -> 实体列表
    facts: List[str]  # 关键事实
    metadata: Dict[str, Any]  # 元数据


class DocumentProcessor:
    """文档处理器"""

    def __init__(self):
        pass

    def load_document(self, file_path: Path) -> DocumentInfo:
        """加载文档"""
        suffix = file_path.suffix.lower()
        content = ""
        page_count = 1

        if suffix in [".txt", ".md"]:
            content = file_path.read_text(encoding="utf-8")
        elif suffix == ".pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(str(file_path))
                page_count = len(reader.pages)
                content = "\n\n".join(
                    [page.extract_text() or "" for page in reader.pages]
                )
            except ImportError:
                raise ImportError("请安装 pypdf: pip install pypdf")
        else:
            content = file_path.read_text(encoding="utf-8")

        return DocumentInfo(
            filename=file_path.name,
            content=content,
            page_count=page_count,
            word_count=len(content),
        )

    def summarize(self, text: str, style: str = "detailed") -> DocumentSummary:
        """生成文档摘要"""
        llm = get_llm(temperature=0.3)

        if style == "brief":
            prompt_text = """请用一句话总结以下文档的核心内容：

{text}

总结（一句话）："""
        else:
            prompt_text = """请对以下文档进行全面分析，输出：
1. 标题（推断或提取）
2. 摘要（200字左右）
3. 关键要点（3-5个）
4. 关键词（5-8个）

文档内容：
{text}

请按以下格式输出：
标题: ...
摘要: ...
要点:
- ...
- ...
关键词: ..., ..., ...
"""

        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | llm | StrOutputParser()

        # 截取前面的内容避免过长
        truncated = text[:8000] if len(text) > 8000 else text
        result = chain.invoke({"text": truncated})

        # 解析结果
        lines = result.strip().split("\n")
        title = ""
        summary = ""
        key_points = []
        keywords = []

        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("标题:") or line.startswith("标题："):
                title = line.split(":", 1)[-1].split("：", 1)[-1].strip()
            elif line.startswith("摘要:") or line.startswith("摘要："):
                summary = line.split(":", 1)[-1].split("：", 1)[-1].strip()
                current_section = "summary"
            elif line.startswith("要点:") or line.startswith("要点："):
                current_section = "points"
            elif line.startswith("关键词:") or line.startswith("关键词："):
                kw_text = line.split(":", 1)[-1].split("：", 1)[-1].strip()
                keywords = [k.strip() for k in kw_text.replace("，", ",").split(",")]
            elif line.startswith("-") and current_section == "points":
                key_points.append(line[1:].strip())
            elif current_section == "summary" and not line.startswith("要点"):
                summary += " " + line

        return DocumentSummary(
            title=title or "未知标题",
            summary=summary.strip(),
            key_points=key_points,
            keywords=keywords,
        )

    def extract_info(self, text: str, extract_types: List[str] = None) -> ExtractedInfo:
        """提取结构化信息"""
        extract_types = extract_types or ["人名", "地名", "组织", "日期", "金额"]

        llm = get_llm(temperature=0.1)
        prompt = ChatPromptTemplate.from_template("""从以下文本中提取信息。

文本：
{text}

请提取以下类型的信息：
{types}

同时列出文本中的关键事实（3-5条）。

请按以下格式输出：
人名: 张三, 李四
地名: 北京, 上海
日期: 2024年1月
...
事实:
- 事实1
- 事实2
""")

        truncated = text[:6000] if len(text) > 6000 else text
        result = chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"text": truncated, "types": ", ".join(extract_types)})

        # 解析结果
        entities = {}
        facts = []
        current_section = None

        for line in result.strip().split("\n"):
            line = line.strip()
            if ":" in line or "：" in line:
                parts = line.replace("：", ":").split(":", 1)
                key = parts[0].strip()
                if key == "事实":
                    current_section = "facts"
                elif key in extract_types:
                    values = [v.strip() for v in parts[1].replace("，", ",").split(",")]
                    entities[key] = [v for v in values if v]
            elif line.startswith("-") and current_section == "facts":
                facts.append(line[1:].strip())

        return ExtractedInfo(
            entities=entities,
            facts=facts,
            metadata={"extract_types": extract_types},
        )

    def compare_documents(self, text1: str, text2: str) -> str:
        """比较两个文档"""
        llm = get_llm(temperature=0.3)
        prompt = ChatPromptTemplate.from_template("""比较以下两个文档的异同：

文档 1：
{text1}

文档 2：
{text2}

请分析：
1. 主要相同点
2. 主要不同点
3. 各自的独特内容

比较结果：""")

        chain = prompt | llm | StrOutputParser()
        t1 = text1[:4000] if len(text1) > 4000 else text1
        t2 = text2[:4000] if len(text2) > 4000 else text2
        return chain.invoke({"text1": t1, "text2": t2})


# 便捷函数
def summarize_file(file_path: str) -> DocumentSummary:
    """快速生成文件摘要"""
    processor = DocumentProcessor()
    doc = processor.load_document(Path(file_path))
    return processor.summarize(doc.content)
