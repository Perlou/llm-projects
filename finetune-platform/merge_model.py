"""
模型合并脚本
将 LoRA 权重合并到基础模型
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console

from scripts.training_utils import load_config
from scripts.model_utils import merge_lora_weights


console = Console()


def main():
    parser = argparse.ArgumentParser(description="合并 LoRA 权重")
    parser.add_argument("--config", "-c", default="config.yaml", help="配置文件")
    parser.add_argument("--adapter", "-a", required=True, help="LoRA 适配器路径")
    parser.add_argument("--output", "-o", required=True, help="输出模型路径")

    args = parser.parse_args()

    console.print("\n[bold blue]🔗 模型合并工具[/bold blue]\n")

    # 加载配置获取基础模型名称
    config = load_config(args.config)
    model_cfg = config.get("model", {})
    base_model = model_cfg.get("name", "Qwen/Qwen2.5-1.5B-Instruct")

    console.print(f"基础模型: {base_model}")
    console.print(f"LoRA 适配器: {args.adapter}")
    console.print(f"输出路径: {args.output}")

    # 合并模型
    merge_lora_weights(
        base_model_name=base_model,
        adapter_path=args.adapter,
        output_path=args.output,
        trust_remote_code=model_cfg.get("trust_remote_code", True),
    )

    console.print(f"\n[green]✅ 模型合并完成: {args.output}[/green]")


if __name__ == "__main__":
    main()
