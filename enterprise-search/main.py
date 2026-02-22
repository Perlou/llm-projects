"""
企业文档搜索引擎 - 主入口
========================

支持混合检索、查询扩展、语义重排序的企业级搜索引擎
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from config import config
from document_processor import DocumentProcessor
from bm25_retriever import BM25Retriever
from vector_retriever import VectorRetriever
from hybrid_search import HybridSearcher
from query_processor import QueryProcessor
from reranker import Reranker
from highlighter import Highlighter
from analytics import SearchAnalytics


console = Console()


class EnterpriseSearchEngine:
    """企业文档搜索引擎"""

    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.bm25 = BM25Retriever()
        self.vector = VectorRetriever()
        self.hybrid = HybridSearcher(self.bm25, self.vector)
        self.query_processor = QueryProcessor()
        self.reranker = Reranker()
        self.highlighter = Highlighter()
        self.analytics = SearchAnalytics()

    def initialize(self) -> bool:
        """初始化搜索引擎"""
        console.print("\n[bold blue]🔍 企业文档搜索引擎 v1.0[/bold blue]\n")

        if not config.validate():
            return False

        # 处理文档
        console.print("索引文档中...", style="dim")
        processed = self.doc_processor.process_directory()

        if not processed:
            console.print("[yellow]⚠️  docs/ 目录为空，请添加文档[/yellow]")
            return True

        # 获取所有文档块
        chunks = self.doc_processor.get_all_chunks()

        # 构建索引
        self.bm25.build_index(chunks)
        self.vector.build_index(chunks)

        stats = self.doc_processor.get_stats()
        console.print(
            f"[green]✅ 已索引 {stats['total_documents']} 个文档，"
            f"{stats['total_chunks']} 个片段[/green]\n"
        )

        return True

    def search(
        self,
        query: str,
        expand_query: bool = True,
        rerank: bool = True,
    ):
        """执行搜索"""
        start_time = time.time()

        # 1. 查询处理
        query_result = self.query_processor.process(query, expand=expand_query)
        expanded_terms = query_result["expanded_terms"]

        # 2. 混合检索
        hybrid_results = self.hybrid.search(query)

        # 获取原始统计
        bm25_count = len(self.bm25.search(query))
        vector_count = len(self.vector.search(query))

        # 3. 重排序
        if rerank and hybrid_results:
            reranked = self.reranker.rerank(query, hybrid_results)
        else:
            reranked = []

        latency_ms = (time.time() - start_time) * 1000

        # 记录分析
        self.analytics.log_search(
            query=query,
            result_count=len(reranked) if reranked else len(hybrid_results),
            latency_ms=latency_ms,
            expanded_terms=expanded_terms,
        )

        # 显示结果
        self._display_results(
            query=query,
            results=reranked,
            bm25_count=bm25_count,
            vector_count=vector_count,
            hybrid_count=len(hybrid_results),
            expanded_terms=expanded_terms,
            latency_ms=latency_ms,
        )

    def _display_results(
        self,
        query: str,
        results,
        bm25_count: int,
        vector_count: int,
        hybrid_count: int,
        expanded_terms: list,
        latency_ms: float,
    ):
        """显示搜索结果"""
        # 检索统计
        console.print("\n[dim][检索统计][/dim]")
        console.print(
            f"  BM25: {bm25_count} 条 | "
            f"向量: {vector_count} 条 | "
            f"融合: {hybrid_count} 条 | "
            f"重排后: {len(results)} 条"
        )
        console.print("━" * 50)

        if not results:
            console.print("[yellow]未找到相关结果[/yellow]")
            return

        # 显示结果
        for result in results:
            doc = result.document
            score = result.relevance_score

            # 文件名
            filename = doc.metadata.get("filename", "未知")
            page = doc.metadata.get("page", None)
            page_info = f" (第 {page + 1} 页)" if page is not None else ""

            # 高亮内容
            highlighted = self.highlighter.highlight(doc.page_content, query, 150)

            console.print(
                f"\n[bold]{result.new_rank}. [{score:.1f}%] {filename}{page_info}[/bold]"
            )
            console.print(f'   [dim]"{highlighted}"[/dim]')

        # 底部信息
        console.print("\n" + "━" * 50)
        console.print(
            f"[dim]耗时: {latency_ms:.0f}ms",
            end="",
        )
        if expanded_terms:
            console.print(f' | 查询扩展: "{", ".join(expanded_terms[:3])}"[/dim]')
        else:
            console.print("[/dim]")

    def show_stats(self):
        """显示统计信息"""
        console.print(self.analytics.format_stats())

    def show_help(self):
        """显示帮助"""
        help_text = """
[bold]命令:[/bold]
  [cyan]/stats[/cyan]    - 查看搜索统计
  [cyan]/help[/cyan]     - 显示帮助
  [cyan]/quit[/cyan]     - 退出程序

[bold]搜索:[/bold]
  直接输入关键词进行搜索
  支持中英文混合搜索
        """
        console.print(Panel(help_text, title="帮助", border_style="blue"))

    def run(self):
        """运行主循环"""
        if not self.initialize():
            return

        console.print("━" * 50)
        self.show_help()

        while True:
            try:
                user_input = console.input("\n[bold blue]搜索:[/bold blue] ").strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    cmd = user_input.lower()

                    if cmd in ["/quit", "/exit", "/q"]:
                        console.print("\n[dim]再见！👋[/dim]\n")
                        break
                    elif cmd == "/stats":
                        self.show_stats()
                    elif cmd == "/help":
                        self.show_help()
                    else:
                        console.print(f"[yellow]未知命令: {cmd}[/yellow]")
                else:
                    self.search(user_input)

            except KeyboardInterrupt:
                console.print("\n\n[dim]再见！👋[/dim]\n")
                break
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")


def main():
    """主函数"""
    engine = EnterpriseSearchEngine()
    engine.run()


if __name__ == "__main__":
    main()
