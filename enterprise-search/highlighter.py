"""
结果高亮模块
对搜索结果进行关键词高亮
"""

import re
from typing import List

import jieba


class Highlighter:
    """结果高亮器"""

    def __init__(self, highlight_start: str = "<mark>", highlight_end: str = "</mark>"):
        self.start = highlight_start
        self.end = highlight_end

    def highlight(self, text: str, query: str, max_length: int = 200) -> str:
        """高亮文本中的关键词"""
        # 提取查询关键词
        keywords = self._extract_keywords(query)

        if not keywords:
            return self._truncate(text, max_length)

        # 找到最佳片段
        snippet = self._find_best_snippet(text, keywords, max_length)

        # 高亮关键词
        highlighted = self._highlight_keywords(snippet, keywords)

        return highlighted

    def _extract_keywords(self, query: str) -> List[str]:
        """提取关键词"""
        # 中文分词
        tokens = list(jieba.cut(query))
        # 过滤短词
        keywords = [t.strip() for t in tokens if len(t.strip()) > 1]
        return keywords

    def _find_best_snippet(
        self, text: str, keywords: List[str], max_length: int
    ) -> str:
        """找到包含最多关键词的片段"""
        text_lower = text.lower()

        # 找到第一个关键词出现的位置
        first_pos = len(text)
        for kw in keywords:
            pos = text_lower.find(kw.lower())
            if pos != -1 and pos < first_pos:
                first_pos = pos

        # 计算片段的起始和结束位置
        half_len = max_length // 2
        start = max(0, first_pos - half_len)
        end = min(len(text), start + max_length)

        # 调整起始位置
        if end - start < max_length:
            start = max(0, end - max_length)

        snippet = text[start:end]

        # 添加省略号
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def _highlight_keywords(self, text: str, keywords: List[str]) -> str:
        """高亮关键词（保持原文大小写）"""
        result = text

        for kw in keywords:
            # 不区分大小写的替换
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            result = pattern.sub(lambda m: f"{self.start}{m.group()}{self.end}", result)

        return result

    def _truncate(self, text: str, max_length: int) -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def to_terminal(self, text: str) -> str:
        """转换为终端格式"""
        # 将 HTML 标记转换为终端颜色
        result = text.replace(self.start, "\033[43m\033[30m")  # 黄底黑字
        result = result.replace(self.end, "\033[0m")
        return result
