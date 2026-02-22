"""
终端显示工具
"""

import json
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt

console = Console()


class Display:
    """终端显示工具类"""

    @staticmethod
    def header():
        """显示应用头部"""
        console.print()
        console.print(
            Panel.fit(
                "[bold cyan]📊 结构化数据提取器[/bold cyan]\n"
                "[dim]Powered by LangChain + Gemini[/dim]",
                border_style="cyan",
            )
        )
        console.print()

    @staticmethod
    def menu(options: list, title: str = "请选择") -> int:
        """显示菜单并获取选择"""
        console.print(f"\n[bold]{title}:[/bold]")
        for i, opt in enumerate(options, 1):
            console.print(f"  [cyan][{i}][/cyan] {opt}")
        console.print("  [dim][q] 退出[/dim]")

        while True:
            choice = Prompt.ask("\n请选择", default="1")
            if choice.lower() == "q":
                return -1
            try:
                idx = int(choice)
                if 1 <= idx <= len(options):
                    return idx - 1
            except ValueError:
                pass
            console.print("[red]无效选择，请重试[/red]")

    @staticmethod
    def multiline_input(prompt: str) -> str:
        """获取多行输入"""
        console.print(f"\n[bold]{prompt}[/bold]")
        console.print("[dim]（输入空行结束）[/dim]")

        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def show_json(data: dict, title: str = "提取结果"):
        """显示 JSON 结果"""
        console.print()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(
            Panel(
                syntax, title=f"[bold green]{title}[/bold green]", border_style="green"
            )
        )
        console.print()

    @staticmethod
    def success(message: str):
        """成功消息"""
        console.print(f"\n[green]✅ {message}[/green]")

    @staticmethod
    def error(message: str):
        """错误消息"""
        console.print(f"\n[red]❌ {message}[/red]")

    @staticmethod
    def info(message: str):
        """信息消息"""
        console.print(f"\n[cyan]ℹ️ {message}[/cyan]")

    @staticmethod
    def loading(message: str = "提取中..."):
        """加载提示"""
        console.print(f"\n[dim]{message}[/dim]")
