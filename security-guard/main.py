"""
LLM 应用安全防护系统 - 主入口
================================

提供多层次的安全检查和防护
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from security_hub import SecurityHub


console = Console()


class SecurityApp:
    """安全检查应用"""

    def __init__(self):
        self.hub = SecurityHub()

    def run(self):
        """运行主循环"""
        console.print("\n[bold blue]🛡️ LLM 安全防护系统 v1.0[/bold blue]\n")

        # 显示状态
        stats = self.hub.get_stats()
        console.print("[dim]已启用的检查模块:[/dim]")
        console.print(f"  • 注入检测: {'✅' if stats['injection_enabled'] else '❌'}")
        console.print(f"  • 越狱防护: {'✅' if stats['jailbreak_enabled'] else '❌'}")
        console.print(f"  • PII 过滤: {'✅' if stats['pii_enabled'] else '❌'}")
        console.print(
            f"  • 内容过滤: {'✅' if stats['content_filter_enabled'] else '❌'}"
        )
        console.print(f"  • 自定义规则: {stats['rules_count']} 条")

        console.print("\n[dim]输入文本进行安全检查，输入 /quit 退出[/dim]")
        console.print("━" * 50)

        while True:
            try:
                user_input = console.input("\n[bold blue]输入:[/bold blue] ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["/quit", "/exit", "/q"]:
                    console.print("\n[dim]再见！👋[/dim]\n")
                    break

                if user_input.startswith("/output "):
                    # 检查输出
                    text = user_input[8:]
                    self._check_output(text)
                else:
                    # 检查输入
                    self._check_input(user_input)

            except KeyboardInterrupt:
                console.print("\n\n[dim]再见！👋[/dim]\n")
                break
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")

    def _check_input(self, text: str):
        """检查输入"""
        result = self.hub.check_input(text)
        self._display_result(result, "输入检查")

    def _check_output(self, text: str):
        """检查输出"""
        result = self.hub.check_output(text)
        self._display_result(result, "输出检查")

    def _display_result(self, result, check_type: str):
        """显示检查结果"""
        console.print(f"\n[bold]🔍 {check_type}结果:[/bold]")

        # 风险等级颜色
        level_colors = {
            "NONE": "green",
            "LOW": "green",
            "MEDIUM": "yellow",
            "HIGH": "red",
            "CRITICAL": "bold red",
        }
        color = level_colors.get(result.risk_level, "white")

        # 状态
        if result.is_safe:
            console.print("  [green]✅ 安全[/green]")
        else:
            console.print(f"  [red]❌ 存在风险[/red]")

        console.print(f"  ⚠️ 风险等级: [{color}]{result.risk_level}[/{color}]")

        # 风险详情
        if result.risks:
            console.print("  📋 检测到的风险:")
            for risk in result.risks:
                console.print(f"     • {risk}")

        # 过滤后的文本
        if result.filtered_text:
            console.print(f"\n  🔒 过滤后: {result.filtered_text}")

        # 详细信息
        if result.injection and result.injection.is_injection:
            console.print(
                f"\n  [dim]注入检测置信度: {result.injection.confidence:.0%}[/dim]"
            )

        if result.jailbreak and result.jailbreak.is_jailbreak:
            console.print(
                f"\n  [dim]越狱攻击类型: {result.jailbreak.attack_type}[/dim]"
            )

        if result.pii and result.pii.has_pii:
            pii_types = set(m.pii_type for m in result.pii.matches)
            console.print(f"\n  [dim]检测到 PII 类型: {', '.join(pii_types)}[/dim]")


def main():
    """主函数"""
    app = SecurityApp()
    app.run()


if __name__ == "__main__":
    main()
