"""
推理测试脚本
测试微调后的模型
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from scripts.model_utils import generate_response


console = Console()


def load_model(model_path: str, use_lora: bool = False, adapter_path: str = None):
    """加载模型"""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    console.print(f"加载模型: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch_dtype,
        device_map="auto",
        trust_remote_code=True,
    )

    if use_lora and adapter_path:
        from peft import PeftModel

        console.print(f"加载 LoRA 适配器: {adapter_path}")
        model = PeftModel.from_pretrained(model, adapter_path)

    return model, tokenizer


def format_prompt(message: str) -> str:
    """格式化提示"""
    return f"<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n"


def main():
    parser = argparse.ArgumentParser(description="模型推理测试")
    parser.add_argument("--model", "-m", required=True, help="模型路径")
    parser.add_argument("--adapter", "-a", help="LoRA 适配器路径（可选）")
    parser.add_argument("--max-tokens", type=int, default=512, help="最大生成长度")
    parser.add_argument("--temperature", type=float, default=0.7, help="温度")

    args = parser.parse_args()

    console.print("\n[bold blue]🧪 模型推理测试[/bold blue]\n")

    # 加载模型
    use_lora = args.adapter is not None
    model, tokenizer = load_model(args.model, use_lora, args.adapter)

    console.print("[green]✅ 模型加载完成[/green]\n")
    console.print("输入问题进行测试，输入 /quit 退出\n")
    console.print("━" * 50)

    while True:
        try:
            user_input = console.input("\n[bold blue]问:[/bold blue] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["/quit", "/exit", "/q"]:
                console.print("\n再见！")
                break

            # 生成响应
            prompt = format_prompt(user_input)

            with console.status("生成中..."):
                response = generate_response(
                    model=model,
                    tokenizer=tokenizer,
                    prompt=prompt,
                    max_new_tokens=args.max_tokens,
                    temperature=args.temperature,
                )

            # 显示响应
            console.print("\n[bold green]答:[/bold green]")
            console.print(Panel(Markdown(response), border_style="green"))

        except KeyboardInterrupt:
            console.print("\n\n再见！")
            break
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")


if __name__ == "__main__":
    main()
