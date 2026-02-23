"""
智能聊天机器人 - 命令行入口
============================

支持流式输出的多轮对话聊天机器人
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich import print as rprint

from config import config
from chat_engine import ChatEngine
from prompts import get_mode_names


console = Console()


class ChatApp:
    """命令行聊天应用"""

    def __init__(self):
        self.engine: ChatEngine = None

    def initialize(self) -> bool:
        """初始化"""
        console.print("\n[bold blue]🤖 智能聊天机器人 v1.0[/bold blue]\n")

        if not config.validate():
            return False

        self.engine = ChatEngine()
        console.print("[green]✅ 初始化完成[/green]\n")
        return True

    def show_help(self):
        """显示帮助"""
        modes = get_mode_names()
        mode_list = "\n".join([f"  • {name}" for name in modes.values()])

        help_text = f"""
[bold]命令:[/bold]
  [cyan]/mode <模式名>[/cyan]  - 切换对话模式
  [cyan]/clear[/cyan]          - 清空对话历史
  [cyan]/export[/cyan]         - 导出对话记录
  [cyan]/tokens[/cyan]         - 显示 token 统计
  [cyan]/help[/cyan]           - 显示帮助
  [cyan]/quit[/cyan]           - 退出程序

[bold]可用模式:[/bold]
{mode_list}
        """
        console.print(Panel(help_text, title="帮助", border_style="blue"))

    def stream_response(self, message: str):
        """流式显示响应"""
        console.print("\n[bold green]🤖 助手:[/bold green] ", end="")

        full_response = ""
        for chunk in self.engine.stream_chat(message):
            console.print(chunk, end="")
            full_response += chunk

        console.print("\n")

    def run(self):
        """运行主循环"""
        if not self.initialize():
            return

        self.show_help()
        console.print("━" * 50)
        console.print(f"[dim]当前模式: {self.engine.mode}[/dim]\n")

        while True:
            try:
                user_input = console.input("[bold blue]👤 你:[/bold blue] ").strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    cmd_parts = user_input.split(maxsplit=1)
                    cmd = cmd_parts[0].lower()

                    if cmd in ["/quit", "/exit", "/q"]:
                        console.print("\n[dim]再见！👋[/dim]\n")
                        break

                    elif cmd == "/help":
                        self.show_help()

                    elif cmd == "/clear":
                        self.engine.clear_history()
                        console.print("[green]✅ 对话历史已清空[/green]")

                    elif cmd == "/tokens":
                        count = self.engine.get_token_count()
                        console.print(f"[dim]当前对话 Token: {count}[/dim]")

                    elif cmd == "/export":
                        content = self.engine.export_history()
                        if content:
                            console.print(Panel(content, title="对话记录"))
                        else:
                            console.print("[yellow]暂无对话记录[/yellow]")

                    elif cmd == "/mode":
                        if len(cmd_parts) > 1:
                            mode = cmd_parts[1]
                            self.engine.change_mode(mode)
                            console.print(f"[green]✅ 已切换到: {mode}[/green]")
                        else:
                            modes = get_mode_names()
                            console.print("[bold]可用模式:[/bold]")
                            for name in modes.values():
                                console.print(f"  • {name}")

                    else:
                        console.print(f"[yellow]未知命令: {cmd}[/yellow]")

                else:
                    self.stream_response(user_input)

            except KeyboardInterrupt:
                console.print("\n\n[dim]再见！👋[/dim]\n")
                break
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")


def main():
    """主函数"""
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()
