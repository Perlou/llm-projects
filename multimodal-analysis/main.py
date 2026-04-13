"""
多模态内容分析平台 - 命令行入口
================================

基于 Gemini 的多模态内容理解与分析应用。
"""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint

from config import config
from analyzers import ImageAnalyzer, ChartAnalyzer, VideoAnalyzer, AudioAnalyzer

console = Console()


class MultimodalApp:
    """多模态分析应用"""

    def __init__(self):
        self.image_analyzer: Optional[ImageAnalyzer] = None
        self.chart_analyzer: Optional[ChartAnalyzer] = None
        self.video_analyzer: Optional[VideoAnalyzer] = None
        self.audio_analyzer: Optional[AudioAnalyzer] = None

    def initialize(self) -> bool:
        """初始化应用"""
        console.print("\n[bold blue]🖼️  多模态内容分析平台 v1.0[/bold blue]")
        console.print("[dim]基于 Gemini 2.0 的智能内容理解[/dim]\n")

        # 验证配置
        if not config.validate():
            return False

        # 初始化分析器
        with console.status("初始化分析器...", spinner="dots"):
            try:
                self.image_analyzer = ImageAnalyzer()
                self.chart_analyzer = ChartAnalyzer()
                self.video_analyzer = VideoAnalyzer()
                self.audio_analyzer = AudioAnalyzer()
            except Exception as e:
                console.print(f"[red]❌ 初始化失败: {e}[/red]")
                return False

        console.print("[green]✅ 系统就绪[/green]\n")
        return True

    def show_help(self):
        """显示帮助"""
        help_text = """
[bold]可用命令:[/bold]

  [cyan]/image <路径>[/cyan]    - 分析图片
  [cyan]/chart <路径>[/cyan]    - 分析图表
  [cyan]/video <路径>[/cyan]    - 分析视频
  [cyan]/audio <路径>[/cyan]    - 分析音频
  [cyan]/search[/cyan]          - 多模态搜索
  [cyan]/help[/cyan]            - 显示帮助
  [cyan]/quit[/cyan]            - 退出程序

[bold]快捷操作:[/bold]

  直接输入文件路径自动识别类型
  支持的格式: jpg/png/gif, mp4/mov, mp3/wav
        """
        console.print(Panel(help_text, title="帮助", border_style="blue"))

    def analyze_image(self, file_path: str):
        """分析图片"""
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]❌ 文件不存在: {file_path}[/red]")
            return

        console.print(f"\n[dim]分析中: {path.name}[/dim]")

        with console.status("图像分析中...", spinner="dots"):
            result = self.image_analyzer.analyze_full(path)

        # 显示结果
        console.print("\n[bold green]📷 图像分析结果[/bold green]")
        console.print("─" * 50)

        if result.description:
            console.print(f"\n[bold]描述:[/bold]\n{result.description}")

        if result.objects:
            console.print("\n[bold]检测到的物体:[/bold]")
            for obj in result.objects[:5]:
                name = obj.get("name", "未知")
                pos = obj.get("position", "")
                console.print(f"  • {name} ({pos})")

        if result.text:
            console.print(f"\n[bold]识别的文字:[/bold]\n{result.text}")

        if result.colors:
            colors = ", ".join(result.colors)
            console.print(f"\n[bold]主要颜色:[/bold] {colors}")

        console.print()

    def analyze_chart(self, file_path: str):
        """分析图表"""
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]❌ 文件不存在: {file_path}[/red]")
            return

        console.print(f"\n[dim]分析中: {path.name}[/dim]")

        with console.status("图表分析中...", spinner="dots"):
            result = self.chart_analyzer.analyze(path)

        # 显示结果
        console.print("\n[bold green]📊 图表分析结果[/bold green]")
        console.print("─" * 50)

        if result.chart_type:
            console.print(f"\n[bold]图表类型:[/bold] {result.chart_type}")

        if result.title:
            console.print(f"[bold]标题:[/bold] {result.title}")

        if result.data:
            console.print("\n[bold]提取的数据:[/bold]")
            table = Table(show_header=True, header_style="bold")
            table.add_column("标签")
            table.add_column("数值", justify="right")
            if any("series" in d for d in result.data):
                table.add_column("系列")

            for item in result.data[:10]:
                label = str(item.get("label", ""))
                value = str(item.get("value", ""))
                if "series" in item:
                    table.add_row(label, value, item.get("series", ""))
                else:
                    table.add_row(label, value)

            console.print(table)

        if result.statistics:
            console.print("\n[bold]统计信息:[/bold]")
            stats = result.statistics
            if "max" in stats:
                console.print(f"  • 最大值: {stats['max']}")
            if "min" in stats:
                console.print(f"  • 最小值: {stats['min']}")
            if "average" in stats:
                console.print(f"  • 平均值: {stats['average']}")

        if result.trend:
            console.print(f"\n[bold]趋势:[/bold] {result.trend}")

        if result.insights:
            console.print("\n[bold]关键洞察:[/bold]")
            for insight in result.insights:
                console.print(f"  📈 {insight}")

        console.print()

    def analyze_video(self, file_path: str):
        """分析视频"""
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]❌ 文件不存在: {file_path}[/red]")
            return

        console.print(f"\n[dim]分析中: {path.name}[/dim]")
        console.print("[dim]提取关键帧并分析，这可能需要一些时间...[/dim]")

        with console.status("视频分析中...", spinner="dots"):
            try:
                result = self.video_analyzer.summarize(path)
            except RuntimeError as e:
                console.print(f"[red]❌ {e}[/red]")
                return

        # 显示结果
        console.print("\n[bold green]🎬 视频分析结果[/bold green]")
        console.print("─" * 50)

        if result.duration:
            minutes = int(result.duration // 60)
            seconds = int(result.duration % 60)
            console.print(f"\n[bold]视频时长:[/bold] {minutes}分{seconds}秒")

        if result.summary:
            console.print(f"\n[bold]内容摘要:[/bold]\n{result.summary}")

        if result.scenes:
            console.print("\n[bold]场景划分:[/bold]")
            for i, scene in enumerate(result.scenes[:5], 1):
                desc = scene.get("description", "")
                time_range = scene.get("estimated_time", "")
                console.print(f"  {i}. {desc} ({time_range})")

        if result.key_frames:
            console.print(f"\n[dim]已分析 {len(result.key_frames)} 个关键帧[/dim]")

        console.print()

    def analyze_audio(self, file_path: str):
        """分析音频"""
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]❌ 文件不存在: {file_path}[/red]")
            return

        console.print(f"\n[dim]分析中: {path.name}[/dim]")

        with console.status("音频转录和分析中...", spinner="dots"):
            result = self.audio_analyzer.analyze(path)

        # 显示结果
        console.print("\n[bold green]🎙️ 音频分析结果[/bold green]")
        console.print("─" * 50)

        if result.duration:
            minutes = int(result.duration // 60)
            seconds = int(result.duration % 60)
            console.print(f"\n[bold]时长:[/bold] {minutes}分{seconds}秒")

        if result.transcript:
            console.print(f"\n[bold]转录文本:[/bold]")
            # 显示前500个字符
            text = result.transcript
            if len(text) > 500:
                text = text[:500] + "..."
            console.print(text)

        if result.summary:
            console.print(f"\n[bold]内容摘要:[/bold]\n{result.summary}")

        if result.keywords:
            keywords = ", ".join(result.keywords)
            console.print(f"\n[bold]关键词:[/bold] {keywords}")

        if result.topics:
            console.print("\n[bold]讨论话题:[/bold]")
            for topic in result.topics:
                console.print(f"  • {topic}")

        console.print()

    def detect_file_type(self, file_path: str) -> Optional[str]:
        """检测文件类型"""
        path = Path(file_path)
        suffix = path.suffix.lower()

        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
        video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
        audio_exts = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}

        if suffix in image_exts:
            return "image"
        elif suffix in video_exts:
            return "video"
        elif suffix in audio_exts:
            return "audio"
        else:
            return None

    def run(self):
        """运行主循环"""
        if not self.initialize():
            return

        console.print("─" * 50)
        self.show_help()
        console.print("─" * 50 + "\n")

        while True:
            try:
                user_input = console.input("[bold blue]> [/bold blue]").strip()

                if not user_input:
                    continue

                # 处理命令
                if user_input.startswith("/"):
                    cmd_parts = user_input.split(maxsplit=1)
                    cmd = cmd_parts[0].lower()
                    arg = cmd_parts[1] if len(cmd_parts) > 1 else ""

                    if cmd in ("/quit", "/exit", "/q"):
                        console.print("\n[dim]再见！👋[/dim]\n")
                        break

                    elif cmd == "/help":
                        self.show_help()

                    elif cmd == "/image":
                        if arg:
                            self.analyze_image(arg)
                        else:
                            console.print("[yellow]用法: /image <文件路径>[/yellow]")

                    elif cmd == "/chart":
                        if arg:
                            self.analyze_chart(arg)
                        else:
                            console.print("[yellow]用法: /chart <文件路径>[/yellow]")

                    elif cmd == "/video":
                        if arg:
                            self.analyze_video(arg)
                        else:
                            console.print("[yellow]用法: /video <文件路径>[/yellow]")

                    elif cmd == "/audio":
                        if arg:
                            self.analyze_audio(arg)
                        else:
                            console.print("[yellow]用法: /audio <文件路径>[/yellow]")

                    elif cmd == "/search":
                        console.print(
                            "[yellow]搜索功能请使用 API 模式 (python app.py)[/yellow]"
                        )

                    else:
                        console.print(f"[yellow]未知命令: {cmd}[/yellow]")

                else:
                    # 尝试作为文件路径处理
                    file_type = self.detect_file_type(user_input)

                    if file_type == "image":
                        # 询问是普通图片还是图表
                        choice = Prompt.ask(
                            "分析类型",
                            choices=["1", "2"],
                            default="1",
                            show_choices=False,
                        )
                        console.print("[dim][1] 普通图片  [2] 图表[/dim]")

                        if choice == "2":
                            self.analyze_chart(user_input)
                        else:
                            self.analyze_image(user_input)

                    elif file_type == "video":
                        self.analyze_video(user_input)

                    elif file_type == "audio":
                        self.analyze_audio(user_input)

                    else:
                        console.print(
                            "[yellow]无法识别的文件类型，请使用命令指定[/yellow]"
                        )

            except KeyboardInterrupt:
                console.print("\n\n[dim]再见！👋[/dim]\n")
                break
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")


def main():
    """主函数"""
    app = MultimodalApp()
    app.run()


if __name__ == "__main__":
    main()
