"""
个人知识库问答系统 - 主入口
============================

基于 RAG 技术的个人文档知识库，支持自然语言问答。
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint

from config import config
from document_loader import DocumentLoader
from text_splitter import TextSplitter
from vector_store import VectorStore
from rag_engine import RAGEngine
from chat import ChatManager


console = Console()


class KnowledgeQA:
    """知识库问答系统"""

    def __init__(self):
        self.doc_loader = DocumentLoader()
        self.text_splitter = TextSplitter()
        self.vector_store = VectorStore()
        self.rag_engine = RAGEngine(self.vector_store)
        self.chat_manager = ChatManager()

    def initialize(self) -> bool:
        """初始化系统"""
        console.print("\n[bold blue]📚 个人知识库问答系统 v1.0[/bold blue]\n")

        # 验证配置
        if not config.validate():
            return False

        # 加载文档
        console.print("加载文档中...", style="dim")
        loaded_docs = self.doc_loader.load_directory(config.docs_dir)

        if not loaded_docs:
            console.print(
                f"[yellow]⚠️  docs/ 目录为空，请添加文档后使用 /add 命令导入[/yellow]"
            )
            return True

        # 处理文档
        all_docs = self.doc_loader.get_all_documents()
        chunks = self.text_splitter.split_documents(all_docs)

        # 存入向量库
        self.vector_store.add_documents(chunks)

        # 显示统计
        stats = self.doc_loader.get_stats()
        split_stats = self.text_splitter.get_stats(chunks)

        console.print(
            f"[green]✅ 已加载 {stats['total_files']} 个文档，"
            f"共 {split_stats['total_chunks']} 个文本片段[/green]\n"
        )

        return True

    def add_document(self, file_path: str):
        """添加新文档"""
        try:
            console.print(f"正在加载: {file_path}...", style="dim")
            loaded = self.doc_loader.load_file(file_path)

            # 分块
            chunks = self.text_splitter.split_documents(loaded.documents)

            # 存入向量库
            self.vector_store.add_documents(chunks)

            console.print(
                f"[green]✅ 已添加 {loaded.filename}，{len(chunks)} 个文本片段[/green]"
            )
        except Exception as e:
            console.print(f"[red]❌ 添加失败: {e}[/red]")

    def list_documents(self):
        """列出已加载的文档"""
        stats = self.doc_loader.get_stats()

        if not stats["files"]:
            console.print("[yellow]暂无已加载的文档[/yellow]")
            return

        table = Table(title="已加载文档")
        table.add_column("文件名", style="cyan")
        table.add_column("类型", style="green")
        table.add_column("页数/段落", justify="right")

        for f in stats["files"]:
            table.add_row(f["name"], f["type"], str(f["pages"]))

        console.print(table)

    def ask(self, question: str):
        """提问"""
        # 获取对话历史
        history = self.chat_manager.get_history()

        # 执行 RAG 查询
        with console.status("思考中...", spinner="dots"):
            response = self.rag_engine.query(question, history)

        # 更新对话历史
        self.chat_manager.add_exchange(question, response.answer)

        # 显示回答
        console.print("\n[bold green]答:[/bold green]", end=" ")
        console.print(Markdown(response.answer))

        # 显示来源
        if response.sources:
            console.print("\n[dim]📖 来源:[/dim]")
            for src in response.sources[:3]:
                page_info = f" (第 {src['page']} 页)" if src["page"] else ""
                console.print(f"  [dim]• {src['filename']}{page_info}[/dim]")

        console.print()

    def show_help(self):
        """显示帮助"""
        help_text = """
[bold]命令:[/bold]
  [cyan]/add <path>[/cyan]  - 添加文档
  [cyan]/list[/cyan]        - 查看已加载文档
  [cyan]/clear[/cyan]       - 清除对话历史
  [cyan]/help[/cyan]        - 显示帮助
  [cyan]/quit[/cyan]        - 退出程序

[bold]提示:[/bold]
  直接输入问题即可开始问答
  支持多轮对话，系统会记住上下文
        """
        console.print(Panel(help_text, title="帮助", border_style="blue"))

    def run(self):
        """运行主循环"""
        if not self.initialize():
            return

        console.print("━" * 50)
        self.show_help()
        console.print("━" * 50 + "\n")

        while True:
            try:
                user_input = console.input("[bold blue]问:[/bold blue] ").strip()

                if not user_input:
                    continue

                # 处理命令
                if user_input.startswith("/"):
                    cmd_parts = user_input.split(maxsplit=1)
                    cmd = cmd_parts[0].lower()

                    if cmd == "/quit" or cmd == "/exit":
                        console.print("\n[dim]再见！👋[/dim]\n")
                        break

                    elif cmd == "/add":
                        if len(cmd_parts) > 1:
                            self.add_document(cmd_parts[1])
                        else:
                            console.print("[yellow]用法: /add <文件路径>[/yellow]")

                    elif cmd == "/list":
                        self.list_documents()

                    elif cmd == "/clear":
                        self.chat_manager.clear_history()
                        console.print("[green]✅ 对话历史已清除[/green]")

                    elif cmd == "/help":
                        self.show_help()

                    else:
                        console.print(f"[yellow]未知命令: {cmd}[/yellow]")

                else:
                    # 正常问答
                    self.ask(user_input)

            except KeyboardInterrupt:
                console.print("\n\n[dim]再见！👋[/dim]\n")
                break
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")


def main():
    """主函数"""
    app = KnowledgeQA()
    app.run()


if __name__ == "__main__":
    main()
