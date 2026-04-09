"""
数据准备脚本
处理和验证训练数据
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.table import Table

from scripts.dataset_utils import (
    load_json,
    save_json,
    convert_alpaca_to_messages,
    convert_sharegpt_to_messages,
    validate_sample,
    split_dataset,
    get_dataset_stats,
    format_prompt,
)


console = Console()


def main():
    parser = argparse.ArgumentParser(description="数据准备脚本")
    parser.add_argument("--input", "-i", required=True, help="输入数据文件路径")
    parser.add_argument("--output", "-o", default="./data/processed", help="输出目录")
    parser.add_argument(
        "--format",
        "-f",
        choices=["alpaca", "sharegpt"],
        default="alpaca",
        help="输入数据格式",
    )
    parser.add_argument("--train-ratio", type=float, default=0.9, help="训练集比例")
    parser.add_argument("--preview", type=int, default=2, help="预览样本数")
    parser.add_argument("--max-samples", type=int, default=None, help="最大样本数")

    args = parser.parse_args()

    console.print("\n[bold blue]📊 数据准备工具[/bold blue]\n")

    # 加载数据
    console.print(f"加载数据: {args.input}")
    try:
        data = load_json(args.input)
    except Exception as e:
        console.print(f"[red]加载失败: {e}[/red]")
        return

    console.print(f"原始样本数: {len(data)}")

    # 限制样本数
    if args.max_samples and len(data) > args.max_samples:
        data = data[: args.max_samples]
        console.print(f"限制后样本数: {len(data)}")

    # 验证数据
    valid_data = []
    for sample in data:
        if validate_sample(sample, args.format):
            valid_data.append(sample)

    console.print(f"有效样本数: {len(valid_data)}")

    if len(valid_data) < len(data):
        console.print(
            f"[yellow]过滤掉 {len(data) - len(valid_data)} 个无效样本[/yellow]"
        )

    # 转换格式
    console.print(f"\n转换格式: {args.format} -> messages")
    converted_data = []

    for sample in valid_data:
        if args.format == "alpaca":
            converted = convert_alpaca_to_messages(sample)
        else:
            converted = convert_sharegpt_to_messages(sample)
        converted_data.append(converted)

    # 分割数据集
    train_data, eval_data = split_dataset(converted_data, args.train_ratio)

    console.print(f"\n数据集分割:")
    console.print(f"  训练集: {len(train_data)} 样本")
    console.print(f"  验证集: {len(eval_data)} 样本")

    # 保存数据
    os.makedirs(args.output, exist_ok=True)

    train_path = os.path.join(args.output, "train.json")
    eval_path = os.path.join(args.output, "eval.json")

    save_json(train_data, train_path)
    save_json(eval_data, eval_path)

    console.print(f"\n[green]✅ 数据保存完成[/green]")
    console.print(f"  训练集: {train_path}")
    console.print(f"  验证集: {eval_path}")

    # 统计信息
    stats = get_dataset_stats(valid_data, args.format)

    table = Table(title="数据集统计")
    table.add_column("指标", style="cyan")
    table.add_column("值", style="green")

    table.add_row("总样本数", str(stats["total_samples"]))
    table.add_row("有效样本数", str(stats["valid_samples"]))
    table.add_row("平均指令长度", str(stats["avg_instruction_len"]))
    table.add_row("平均输出长度", str(stats["avg_output_len"]))

    console.print("\n")
    console.print(table)

    # 预览样本
    if args.preview > 0:
        console.print(f"\n[bold]样本预览:[/bold]\n")
        for i, sample in enumerate(valid_data[: args.preview]):
            console.print(f"--- 样本 {i + 1} ---")
            console.print(format_prompt(sample, args.format))
            console.print()


if __name__ == "__main__":
    main()
