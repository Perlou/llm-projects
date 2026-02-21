"""
写作模式定义
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class WritingMode(Enum):
    BLOG = "blog"
    EMAIL = "email"
    COPYWRITING = "copywriting"
    CODE_DOCS = "code_docs"


@dataclass
class StyleOption:
    """风格选项"""

    name: str
    description: str
    prompt_modifier: str


@dataclass
class WritingModeConfig:
    """写作模式配置"""

    name: str
    emoji: str
    description: str
    styles: List[StyleOption]


# 写作模式配置
WRITING_MODES: Dict[WritingMode, WritingModeConfig] = {
    WritingMode.BLOG: WritingModeConfig(
        name="博客文章",
        emoji="📝",
        description="撰写技术博客、教程或观点文章",
        styles=[
            StyleOption(
                "技术文档", "专业严谨的技术文档风格", "professional and technical"
            ),
            StyleOption("趣味教程", "轻松有趣的教学风格", "fun and engaging tutorial"),
            StyleOption("观点评论", "有深度的观点分析", "insightful opinion piece"),
        ],
    ),
    WritingMode.EMAIL: WritingModeConfig(
        name="邮件写作",
        emoji="✉️",
        description="撰写商务邮件、感谢信或请求邮件",
        styles=[
            StyleOption("商务正式", "正式的商务邮件", "formal business"),
            StyleOption("友好亲切", "友好的日常邮件", "friendly and warm"),
            StyleOption("简洁高效", "简短高效的沟通", "brief and efficient"),
        ],
    ),
    WritingMode.COPYWRITING: WritingModeConfig(
        name="文案创作",
        emoji="📢",
        description="撰写产品文案、广告语或社交媒体内容",
        styles=[
            StyleOption("创意吸睛", "有创意的营销文案", "creative and catchy"),
            StyleOption("专业可信", "专业可靠的介绍", "professional and trustworthy"),
            StyleOption("情感共鸣", "引发情感共鸣", "emotional and relatable"),
        ],
    ),
    WritingMode.CODE_DOCS: WritingModeConfig(
        name="代码文档",
        emoji="📖",
        description="生成代码注释、README或API文档",
        styles=[
            StyleOption("详细说明", "详细的代码文档", "detailed and comprehensive"),
            StyleOption("简洁注释", "简洁的代码注释", "concise comments"),
            StyleOption("示例丰富", "包含丰富示例", "example-rich documentation"),
        ],
    ),
}
