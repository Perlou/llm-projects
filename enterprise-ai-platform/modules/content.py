"""
内容创作模块
============

多风格内容生成和优化。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from services.llm_provider import get_llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


class ContentStyle(str, Enum):
    """内容风格"""

    FORMAL = "formal"  # 正式
    CASUAL = "casual"  # 轻松
    TECHNICAL = "technical"  # 技术
    MARKETING = "marketing"  # 营销
    ACADEMIC = "academic"  # 学术


class ContentType(str, Enum):
    """内容类型"""

    ARTICLE = "article"  # 文章
    BLOG = "blog"  # 博客
    EMAIL = "email"  # 邮件
    REPORT = "report"  # 报告
    SOCIAL = "social"  # 社交媒体


@dataclass
class GeneratedContent:
    """生成的内容"""

    title: str
    content: str
    word_count: int
    style: str
    content_type: str
    suggestions: List[str] = None


class ContentCreator:
    """内容创作器"""

    STYLE_PROMPTS = {
        ContentStyle.FORMAL: "使用正式、专业的语言，避免口语化表达。",
        ContentStyle.CASUAL: "使用轻松、亲切的语言，可以适当使用表情符号。",
        ContentStyle.TECHNICAL: "使用准确的技术术语，注重逻辑性和准确性。",
        ContentStyle.MARKETING: "使用有吸引力的语言，突出价值和好处，引导行动。",
        ContentStyle.ACADEMIC: "使用学术规范的语言，注重引用和论证。",
    }

    TYPE_TEMPLATES = {
        ContentType.ARTICLE: "请撰写一篇完整的文章，包含引言、正文和结论。",
        ContentType.BLOG: "请撰写一篇博客文章，注重可读性和个人观点。",
        ContentType.EMAIL: "请撰写一封邮件，包含称呼、正文和落款。",
        ContentType.REPORT: "请撰写一份报告，使用清晰的结构和小标题。",
        ContentType.SOCIAL: "请撰写社交媒体内容，简洁有力，适合分享。",
    }

    def __init__(self):
        pass

    def generate(
        self,
        topic: str,
        content_type: ContentType = ContentType.ARTICLE,
        style: ContentStyle = ContentStyle.CASUAL,
        length: str = "medium",  # short, medium, long
        additional_requirements: str = "",
    ) -> GeneratedContent:
        """生成内容"""
        llm = get_llm(temperature=0.7)

        length_guide = {
            "short": "300-500字",
            "medium": "800-1200字",
            "long": "1500-2500字",
        }

        prompt = ChatPromptTemplate.from_template("""你是一位专业的内容创作者。

主题：{topic}

要求：
- 类型：{type_desc}
- 风格：{style_desc}
- 长度：{length}
- 其他要求：{additional}

请创作高质量的内容，确保：
1. 标题吸引人
2. 结构清晰
3. 内容有价值
4. 符合指定风格

创作内容（先输出标题，然后是正文）：""")

        chain = prompt | llm | StrOutputParser()
        result = chain.invoke(
            {
                "topic": topic,
                "type_desc": self.TYPE_TEMPLATES.get(content_type, ""),
                "style_desc": self.STYLE_PROMPTS.get(style, ""),
                "length": length_guide.get(length, "适中"),
                "additional": additional_requirements or "无",
            }
        )

        # 解析结果
        lines = result.strip().split("\n")
        title = lines[0].lstrip("#").strip() if lines else topic
        content = "\n".join(lines[1:]).strip() if len(lines) > 1 else result

        return GeneratedContent(
            title=title,
            content=content,
            word_count=len(content),
            style=style.value,
            content_type=content_type.value,
        )

    def improve(self, content: str, improvement_type: str = "general") -> str:
        """改进内容"""
        llm = get_llm(temperature=0.5)

        improvement_prompts = {
            "general": "全面优化这段内容，提升可读性和表达效果。",
            "clarity": "让这段内容更加清晰易懂，消除歧义。",
            "engagement": "让这段内容更吸引人，增加读者兴趣。",
            "concise": "精简这段内容，去除冗余，保留核心信息。",
            "seo": "优化这段内容以提升搜索引擎排名，添加关键词。",
        }

        prompt = ChatPromptTemplate.from_template("""请优化以下内容：

原始内容：
{content}

优化方向：{direction}

优化后的内容：""")

        chain = prompt | llm | StrOutputParser()
        return chain.invoke(
            {
                "content": content,
                "direction": improvement_prompts.get(
                    improvement_type, improvement_prompts["general"]
                ),
            }
        )

    def expand(self, outline: str) -> str:
        """根据大纲扩展内容"""
        llm = get_llm(temperature=0.6)

        prompt = ChatPromptTemplate.from_template("""请根据以下大纲展开写作：

大纲：
{outline}

请为每个要点撰写2-3段内容，形成完整的文章。

完整内容：""")

        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"outline": outline})

    def rewrite(
        self,
        content: str,
        target_style: ContentStyle,
    ) -> str:
        """按指定风格改写"""
        llm = get_llm(temperature=0.5)

        prompt = ChatPromptTemplate.from_template("""请将以下内容改写为{style}风格：

原始内容：
{content}

风格要求：{style_desc}

改写后的内容：""")

        chain = prompt | llm | StrOutputParser()
        return chain.invoke(
            {
                "content": content,
                "style": target_style.value,
                "style_desc": self.STYLE_PROMPTS.get(target_style, ""),
            }
        )

    def generate_outline(self, topic: str, sections: int = 5) -> List[str]:
        """生成内容大纲"""
        llm = get_llm(temperature=0.5)

        prompt = ChatPromptTemplate.from_template("""为以下主题生成内容大纲：

主题：{topic}
章节数：{sections}

请生成清晰的大纲，每个章节用一行表示，格式为：
1. 章节标题
2. 章节标题
...

大纲：""")

        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"topic": topic, "sections": sections})

        # 解析大纲
        outlines = []
        for line in result.strip().split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                # 移除序号
                clean = line.lstrip("0123456789.-").strip()
                if clean:
                    outlines.append(clean)

        return outlines[:sections]


# 便捷函数
def create_article(topic: str, style: str = "casual") -> str:
    """快速创建文章"""
    creator = ContentCreator()
    style_enum = (
        ContentStyle(style)
        if style in [s.value for s in ContentStyle]
        else ContentStyle.CASUAL
    )
    result = creator.generate(topic, ContentType.ARTICLE, style_enum)
    return f"# {result.title}\n\n{result.content}"
