"""
内容过滤模块
"""

import re
from typing import List, Set
from dataclasses import dataclass


@dataclass
class ContentCheckResult:
    """内容检查结果"""

    is_safe: bool
    flagged_categories: List[str]
    confidence: float
    details: str


class ContentFilter:
    """内容过滤器"""

    # 违规内容类别
    CONTENT_CATEGORIES = {
        "violence": {
            "keywords": [
                "杀人",
                "暴力",
                "伤害",
                "攻击",
                "武器",
                "kill",
                "murder",
                "attack",
                "weapon",
                "violence",
            ],
            "patterns": [
                r"如何(制作|制造)(炸弹|武器|毒药)",
                r"how to (make|build) (bomb|weapon|poison)",
            ],
        },
        "illegal": {
            "keywords": [
                "毒品",
                "赌博",
                "洗钱",
                "诈骗",
                "drugs",
                "gambling",
                "fraud",
                "scam",
            ],
            "patterns": [
                r"购买.*(毒品|违禁品)",
                r"如何.*(诈骗|洗钱)",
            ],
        },
        "harassment": {
            "keywords": [
                "骚扰",
                "辱骂",
                "歧视",
                "仇恨",
                "harass",
                "abuse",
                "discriminate",
                "hate",
            ],
            "patterns": [],
        },
        "adult": {
            "keywords": [
                "色情",
                "成人内容",
            ],
            "patterns": [],
        },
    }

    def __init__(self, enabled_categories: List[str] = None):
        """
        初始化过滤器

        Args:
            enabled_categories: 启用的类别，None 表示全部启用
        """
        self.categories = {}

        for category, config in self.CONTENT_CATEGORIES.items():
            if enabled_categories is None or category in enabled_categories:
                keywords = set(w.lower() for w in config["keywords"])
                patterns = [re.compile(p, re.IGNORECASE) for p in config["patterns"]]
                self.categories[category] = {
                    "keywords": keywords,
                    "patterns": patterns,
                }

    def check(self, text: str) -> ContentCheckResult:
        """检查内容"""
        text_lower = text.lower()
        flagged = []
        max_confidence = 0.0

        for category, config in self.categories.items():
            # 关键词匹配
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    flagged.append(category)
                    max_confidence = max(max_confidence, 0.8)
                    break

            # 模式匹配
            for pattern in config["patterns"]:
                if pattern.search(text):
                    if category not in flagged:
                        flagged.append(category)
                    max_confidence = max(max_confidence, 0.9)
                    break

        # 去重
        flagged = list(set(flagged))

        return ContentCheckResult(
            is_safe=len(flagged) == 0,
            flagged_categories=flagged,
            confidence=max_confidence,
            details=f"检测到 {len(flagged)} 个违规类别" if flagged else "内容安全",
        )

    def add_keywords(self, category: str, keywords: List[str]):
        """添加关键词"""
        if category in self.categories:
            self.categories[category]["keywords"].update(w.lower() for w in keywords)

    def add_pattern(self, category: str, pattern: str):
        """添加模式"""
        if category in self.categories:
            self.categories[category]["patterns"].append(
                re.compile(pattern, re.IGNORECASE)
            )

    def get_categories(self) -> List[str]:
        """获取所有类别"""
        return list(self.categories.keys())
