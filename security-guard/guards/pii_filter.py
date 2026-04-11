"""
敏感信息过滤模块 (PII Filter)
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class PIIMatch:
    """PII 匹配结果"""

    pii_type: str
    original: str
    masked: str
    start: int
    end: int


@dataclass
class PIIResult:
    """PII 检测结果"""

    has_pii: bool
    matches: List[PIIMatch]
    filtered_text: str


class PIIFilter:
    """敏感信息过滤器"""

    # PII 模式定义
    PII_PATTERNS = {
        "EMAIL": (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL]"),
        "PHONE": (r"(?:(?:\+|00)86)?1[3-9]\d{9}", "[PHONE]"),
        "ID_CARD": (
            r"[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]",
            "[ID_CARD]",
        ),
        "BANK_CARD": (r"(?:62|45|52|53|55|60)\d{14,17}", "[BANK_CARD]"),
        "IP_ADDRESS": (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP]"),
        "URL": (r"https?://[^\s<>\"{}|\\^`\[\]]+", "[URL]"),
        "ADDRESS": (
            r"[\u4e00-\u9fa5]{2,}(?:省|市|区|县|镇|村|路|街|号|楼|室)",
            "[ADDRESS]",
        ),
    }

    def __init__(self, enabled_types: List[str] = None):
        """
        初始化过滤器

        Args:
            enabled_types: 启用的 PII 类型，None 表示全部启用
        """
        self.patterns = {}
        for pii_type, (pattern, mask) in self.PII_PATTERNS.items():
            if enabled_types is None or pii_type in enabled_types:
                self.patterns[pii_type] = (re.compile(pattern), mask)

    def detect(self, text: str) -> List[PIIMatch]:
        """检测 PII"""
        matches = []

        for pii_type, (pattern, mask) in self.patterns.items():
            for match in pattern.finditer(text):
                matches.append(
                    PIIMatch(
                        pii_type=pii_type,
                        original=match.group(),
                        masked=mask,
                        start=match.start(),
                        end=match.end(),
                    )
                )

        # 按位置排序
        matches.sort(key=lambda x: x.start)
        return matches

    def filter(self, text: str) -> PIIResult:
        """过滤 PII"""
        matches = self.detect(text)

        if not matches:
            return PIIResult(
                has_pii=False,
                matches=[],
                filtered_text=text,
            )

        # 从后往前替换，避免位置偏移
        filtered = text
        for match in reversed(matches):
            filtered = filtered[: match.start] + match.masked + filtered[match.end :]

        return PIIResult(
            has_pii=True,
            matches=matches,
            filtered_text=filtered,
        )

    def get_summary(self, matches: List[PIIMatch]) -> Dict[str, int]:
        """获取 PII 统计"""
        summary = {}
        for match in matches:
            summary[match.pii_type] = summary.get(match.pii_type, 0) + 1
        return summary

    def add_pattern(self, pii_type: str, pattern: str, mask: str):
        """添加自定义模式"""
        self.patterns[pii_type] = (re.compile(pattern), mask)

    def get_enabled_types(self) -> List[str]:
        """获取启用的 PII 类型"""
        return list(self.patterns.keys())
