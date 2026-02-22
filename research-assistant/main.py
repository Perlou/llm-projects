"""
自动化研究助手 - 主入口
=========================

使用 ReAct Agent 实现自动搜索、阅读、总结的研究助手
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint

from config import config
from agent import ResearchAgent
from tools.note import note_manager


console = Console()


class ResearchAssistantApp:
    """研究助手应用"""

    def __init__(self):
        self.agent: ResearchAgent = None

    def initialize(self) -> bool:
        """初始化应用"""
        console.print("\n[bold blue]🔬 自动化研究助手 v1.0[/bold blue]\n")

        if not config.validate():
            return False

        console.print("初始化 Agent...", style="dim")
        self.agent = ResearchAgent()
        console.print("[green]✅ Agent 初始化完成[/green]\n")

        return True

    def show_help(self):
        """显示帮助"""
        help_text = """
[bold]使用方法:[/bold]
  直接输入研究任务或问题，Agent 会自动搜索、阅读、整理资料

[bold]命令:[/bold]
  [cyan]/notes[/cyan]     - 查看已记录的笔记
  [cyan]/reports[/cyan]   - 查看生成的报告
  [cyan]/clear[/cyan]     - 清空笔记和重置 Agent
  [cyan]/help[/cyan]      - 显示帮助
  [cyan]/quit[/cyan]      - 退出程序

[bold]示例任务:[/bold]
  • 调研 RAG 技术的最新进展
  • 了解 LangChain Agent 的工作原理
  • 总结 Transformer 架构的核心思想
        """
        console.print(Panel(help_text, title="帮助", border_style="blue"))

    def show_notes(self):
        """显示笔记"""
        notes = note_manager.list_notes()

        if not notes:
            console.print("[yellow]暂无笔记[/yellow]")
            return

        console.print("\n[bold]📒 已记录的笔记:[/bold]\n")
        for note in notes:
            console.print(f"[cyan]{note['id']}. {note['title']}[/cyan]")
            console.print(f"   {note['content'][:100]}...")
            console.print()

    def show_reports(self):
        """显示报告列表"""
        import os

        reports = []
        if os.path.exists(config.reports_dir):
            reports = [f for f in os.listdir(config.reports_dir) if f.endswith(".md")]

        if not reports:
            console.print("[yellow]暂无报告[/yellow]")
            return

        console.print("\n[bold]📝 已生成的报告:[/bold]\n")
        for report in sorted(reports, reverse=True):
            console.print(f"  • {report}")
        console.print(f"\n[dim]报告目录: {config.reports_dir}[/dim]")

    def execute_task(self, task: str):
        """执行研究任务"""
        console.print(f"\n[bold]📋 任务:[/bold] {task}\n")
        console.print("━" * 50)

        with console.status("[bold green]Agent 执行中...[/bold green]"):
            result = self.agent.run(task)

        console.print("━" * 50)
        console.print("\n[bold green]✅ 任务完成[/bold green]\n")

        # 显示结果
        console.print(Panel(Markdown(result), title="研究结果", border_style="green"))

        # 显示统计
        notes = note_manager.list_notes()
        console.print(f"\n[dim]📒 共记录 {len(notes)} 条笔记[/dim]")

    def run(self):
        """运行主循环"""
        if not self.initialize():
            return

        console.print("输入研究任务或问题，我会帮你搜索、阅读、整理资料。")
        console.print("━" * 50)
        self.show_help()

        while True:
            try:
                user_input = console.input("\n[bold blue]任务:[/bold blue] ").strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    cmd = user_input.lower()

                    if cmd in ["/quit", "/exit", "/q"]:
                        console.print("\n[dim]再见！👋[/dim]\n")
                        break

                    elif cmd == "/notes":
                        self.show_notes()

                    elif cmd == "/reports":
                        self.show_reports()

                    elif cmd == "/clear":
                        self.agent.reset()
                        console.print("[green]✅ 已清空笔记并重置 Agent[/green]")

                    elif cmd == "/help":
                        self.show_help()

                    else:
                        console.print(f"[yellow]未知命令: {cmd}[/yellow]")

                else:
                    self.execute_task(user_input)

            except KeyboardInterrupt:
                console.print("\n\n[dim]再见！👋[/dim]\n")
                break
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")


def main():
    """主函数"""
    app = ResearchAssistantApp()
    app.run()


if __name__ == "__main__":
    main()
