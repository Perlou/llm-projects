"""
网络搜索工具
使用 DuckDuckGo 进行网络搜索
"""

from typing import List, Dict, Any
from langchain_core.tools import BaseTool
from pydantic import Field

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


class SearchTool(BaseTool):
    """网络搜索工具"""

    name: str = "search"
    description: str = """搜索网络获取信息。
当你需要查找最新资料、论文、新闻或任何网络上的信息时使用此工具。
输入应该是搜索查询字符串。"""

    max_results: int = Field(default=5)

    def _run(self, query: str) -> str:
        """执行搜索"""
        if DDGS is None:
            return "搜索工具未正确安装，请安装 duckduckgo-search 包"

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))

            if not results:
                return f"未找到关于 '{query}' 的搜索结果"

            # 格式化结果
            formatted = []
            for i, r in enumerate(results, 1):
                formatted.append(
                    f"{i}. {r.get('title', '无标题')}\n"
                    f"   链接: {r.get('href', '')}\n"
                    f"   摘要: {r.get('body', '')[:200]}..."
                )

            return f"搜索 '{query}' 找到 {len(results)} 条结果:\n\n" + "\n\n".join(
                formatted
            )

        except Exception as e:
            return f"搜索失败: {str(e)}"

    async def _arun(self, query: str) -> str:
        """异步执行"""
        return self._run(query)


def create_search_tool(max_results: int = 5) -> SearchTool:
    """创建搜索工具实例"""
    return SearchTool(max_results=max_results)
