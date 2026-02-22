"""
网页阅读工具
读取和解析网页内容
"""

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify
from langchain_core.tools import BaseTool
from pydantic import Field


class ReaderTool(BaseTool):
    """网页阅读工具"""

    name: str = "read_url"
    description: str = """阅读指定 URL 的网页内容。
当你需要深入阅读某篇文章、论文或网页时使用此工具。
输入应该是完整的 URL 地址。"""

    max_length: int = Field(default=3000)
    timeout: int = Field(default=10)

    def _run(self, url: str) -> str:
        """读取网页"""
        try:
            # 请求网页
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()

            # 解析 HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # 移除不需要的元素
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # 提取标题
            title = soup.find("title")
            title_text = title.get_text().strip() if title else "无标题"

            # 提取正文
            # 尝试常见的文章容器
            article = (
                soup.find("article")
                or soup.find("main")
                or soup.find("div", class_="content")
                or soup.find("body")
            )

            if article:
                # 转换为 Markdown
                content = markdownify(str(article), heading_style="ATX")
            else:
                content = soup.get_text()

            # 清理和截断
            content = self._clean_text(content)
            if len(content) > self.max_length:
                content = content[: self.max_length] + "\n\n...[内容已截断]"

            return f"📄 {title_text}\n来源: {url}\n\n{content}"

        except httpx.TimeoutException:
            return f"读取超时: {url}"
        except httpx.HTTPError as e:
            return f"HTTP 错误: {str(e)}"
        except Exception as e:
            return f"读取失败: {str(e)}"

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        import re

        # 移除多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        # 移除多余空格
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    async def _arun(self, url: str) -> str:
        """异步执行"""
        return self._run(url)


def create_reader_tool(max_length: int = 3000) -> ReaderTool:
    """创建阅读工具实例"""
    return ReaderTool(max_length=max_length)
