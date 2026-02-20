"""
终端界面
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from typing import Optional

from models import ChatResponse
from utils import format_cost, format_time, format_tokens


console = Console()


def print_welcome():
    """打印欢迎信息"""
    console.print()
    console.print(
        Panel.fit(
            "[bold blue]🤖 多模型对比聊天应用[/bold blue]\n"
            "[dim]输入问题，按 Enter 发送，输入 'quit' 或 'exit' 退出[/dim]",
            border_style="blue",
        )
    )
    console.print()


def print_model_list(models: list[str], available: dict[str, bool]):
    """打印可用模型列表"""
    table = Table(title="📦 已加载模型", show_header=True, header_style="bold")
    table.add_column("模型", style="cyan")
    table.add_column("状态")

    for model in models:
        status = (
            "[green]✓ 可用[/green]" if available.get(model) else "[red]✗ 不可用[/red]"
        )
        table.add_row(model, status)

    console.print(table)
    console.print()


def print_user_input(message: str):
    """打印用户输入"""
    console.print(f"\n[bold green]👤 你:[/bold green] {message}\n")


def create_response_panel(
    response: ChatResponse, streaming_content: str = None
) -> Panel:
    """创建响应面板"""
    content = streaming_content if streaming_content is not None else response.content

    if response.error:
        # 错误状态
        body = f"[red]❌ 错误: {response.error}[/red]"
        title = f"[red]{response.model}[/red]"
    else:
        # 正常状态
        body = content if content else "[dim]等待响应...[/dim]"

        # 添加统计信息
        if response.total_time > 0:
            stats_line = f"\n\n[dim]📊 {format_time(response.total_time)}"
            if response.output_tokens > 0:
                stats_line += f" | {format_tokens(response.output_tokens)} tokens"
            if response.cost > 0:
                stats_line += f" | 💰 {format_cost(response.cost)}"
            stats_line += "[/dim]"
            body += stats_line

        title = f"[bold cyan]{response.model}[/bold cyan]"
        if response.first_token_time > 0:
            title += f" [dim]({format_time(response.first_token_time)})[/dim]"

    return Panel(
        body,
        title=title,
        border_style="cyan" if not response.error else "red",
        expand=True,
    )


def print_responses(responses: list[ChatResponse]):
    """打印所有响应"""
    for response in responses:
        console.print(create_response_panel(response))
        console.print()


def print_comparison_table(responses: list[ChatResponse]):
    """打印对比表格"""
    table = Table(title="📊 性能对比", show_header=True, header_style="bold")
    table.add_column("模型", style="cyan")
    table.add_column("首字延迟", justify="right")
    table.add_column("总耗时", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("速度", justify="right")
    table.add_column("成本", justify="right")

    for r in responses:
        if r.error:
            table.add_row(r.model, "-", "-", "-", "-", "[red]错误[/red]")
        else:
            speed = (
                f"{r.output_tokens / r.total_time:.1f}/s" if r.total_time > 0 else "-"
            )
            table.add_row(
                r.model,
                format_time(r.first_token_time),
                format_time(r.total_time),
                format_tokens(r.output_tokens),
                speed,
                format_cost(r.cost),
            )

    console.print()
    console.print(table)


def get_user_input() -> str:
    """获取用户输入"""
    try:
        return console.input("[bold green]👤 你:[/bold green] ").strip()
    except (EOFError, KeyboardInterrupt):
        return "quit"


def print_goodbye():
    """打印再见信息"""
    console.print("\n[dim]👋 再见！[/dim]\n")


def print_error(message: str):
    """打印错误信息"""
    console.print(f"[red]❌ {message}[/red]")


def print_info(message: str):
    """打印提示信息"""
    console.print(f"[dim]ℹ️ {message}[/dim]")
