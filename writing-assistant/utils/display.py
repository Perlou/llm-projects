"""
终端显示工具
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt
from rich.live import Live


console = Console()


class Display:
    """终端显示工具类"""

    @staticmethod
    def header():
        """显示应用头部"""
        console.print()
        console.print(
            Panel.fit(
                "[bold cyan]🖊️ 智能写作助手[/bold cyan]\n[dim]Powered by Gemini[/dim]",
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
        console.print(f"  [dim][q] 退出[/dim]")

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
    def input(prompt: str) -> str:
        """获取用户输入"""
        return Prompt.ask(f"\n[bold]{prompt}[/bold]")

    @staticmethod
    def stream_output(text_generator):
        """流式输出文本"""
        console.print("\n[dim]生成中...[/dim]\n")

        full_text = ""
        with Live(console=console, refresh_per_second=10) as live:
            for chunk in text_generator:
                full_text += chunk
                live.update(Markdown(full_text))

        console.print()
        return full_text

    @staticmethod
    def output(text: str):
        """输出 Markdown 内容"""
        console.print()
        console.print(Markdown(text))
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
    def save_prompt() -> bool:
        """询问是否保存"""
        choice = Prompt.ask("\n保存到文件?", choices=["y", "n"], default="n")
        return choice.lower() == "y"

    @staticmethod
    def get_filename() -> str:
        """获取保存文件名"""
        return Prompt.ask("文件名", default="output.md")
