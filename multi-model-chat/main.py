#!/usr/bin/env python3
"""
多模型对比聊天应用

Usage:
    python main.py                          # 交互模式
    python main.py --query "你的问题"       # 单次查询
    python main.py --models gpt-4 claude-3-sonnet --query "你好"
"""

import asyncio
import argparse
import sys
from typing import Optional

from config import MODELS, get_api_key, get_default_models, get_ollama_host
from models import (
    BaseModel,
    ChatMessage,
    ChatResponse,
    OpenAIModel,
    ClaudeModel,
    GeminiModel,
    OllamaModel,
)
from ui import (
    print_welcome,
    print_model_list,
    print_user_input,
    print_responses,
    print_comparison_table,
    get_user_input,
    print_goodbye,
    print_error,
    print_info,
)


def create_model(model_key: str) -> Optional[BaseModel]:
    """根据模型 key 创建模型实例"""
    if model_key not in MODELS:
        print_error(f"未知模型: {model_key}")
        return None

    config = MODELS[model_key]
    provider = config.provider

    # 获取 API Key
    api_key = get_api_key(provider)

    # 根据提供商创建模型
    if provider == "openai":
        if not api_key:
            print_info(f"跳过 {model_key}: 未配置 OPENAI_API_KEY")
            return None
        return OpenAIModel(
            api_key=api_key,
            name=config.name,
            provider=provider,
            model_id=config.model_id,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            input_price=config.input_price,
            output_price=config.output_price,
        )

    elif provider == "anthropic":
        if not api_key:
            print_info(f"跳过 {model_key}: 未配置 ANTHROPIC_API_KEY")
            return None
        return ClaudeModel(
            api_key=api_key,
            name=config.name,
            provider=provider,
            model_id=config.model_id,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            input_price=config.input_price,
            output_price=config.output_price,
        )

    elif provider == "gemini":
        if not api_key:
            print_info(f"跳过 {model_key}: 未配置 GOOGLE_API_KEY")
            return None
        return GeminiModel(
            api_key=api_key,
            name=config.name,
            provider=provider,
            model_id=config.model_id,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            input_price=config.input_price,
            output_price=config.output_price,
        )

    elif provider == "ollama":
        return OllamaModel(
            host=get_ollama_host(),
            name=config.name,
            provider=provider,
            model_id=config.model_id,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            input_price=config.input_price,
            output_price=config.output_price,
        )

    return None


async def query_models(
    models: list[BaseModel],
    message: str,
    system_prompt: str = None,
) -> list[ChatResponse]:
    """并发查询多个模型"""

    # 构建消息
    messages = []
    if system_prompt:
        messages.append(ChatMessage(role="system", content=system_prompt))
    messages.append(ChatMessage(role="user", content=message))

    # 并发调用所有模型
    tasks = [model.chat(messages) for model in models]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理异常
    results = []
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            results.append(
                ChatResponse(
                    content="",
                    model=models[i].name,
                    provider=models[i].provider,
                    error=str(response),
                )
            )
        else:
            results.append(response)

    return results


async def interactive_mode(models: list[BaseModel]):
    """交互模式"""
    print_welcome()

    # 显示可用模型
    model_names = [m.name for m in models]
    print_info(f"已加载 {len(models)} 个模型: {', '.join(model_names)}")
    print()

    system_prompt = "你是一个有帮助的助手，回答简洁清晰。"

    while True:
        # 获取用户输入
        user_input = get_user_input()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print_goodbye()
            break

        if user_input.lower() == "help":
            print_info("输入问题进行多模型对比，输入 'quit' 退出")
            continue

        # 查询所有模型
        print_user_input(user_input)
        print_info("正在查询多个模型...\n")

        responses = await query_models(models, user_input, system_prompt)

        # 显示响应
        print_responses(responses)

        # 显示对比表格
        print_comparison_table(responses)
        print()


async def single_query_mode(models: list[BaseModel], query: str):
    """单次查询模式"""
    print_user_input(query)
    print_info("正在查询多个模型...\n")

    responses = await query_models(models, query)

    print_responses(responses)
    print_comparison_table(responses)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="多模型对比聊天应用",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                                    # 交互模式
  python main.py --query "什么是机器学习？"         # 单次查询
  python main.py --models gpt-4 claude-3-sonnet    # 指定模型
  python main.py --list-models                      # 列出可用模型
        """,
    )

    parser.add_argument("--query", "-q", type=str, help="单次查询的问题")

    parser.add_argument("--models", "-m", nargs="+", help="要使用的模型（空格分隔）")

    parser.add_argument("--list-models", action="store_true", help="列出所有可用模型")

    return parser.parse_args()


def list_available_models():
    """列出所有可用模型"""
    print("\n📦 可用模型列表:\n")

    for key, config in MODELS.items():
        api_key = get_api_key(config.provider)
        status = "✓" if api_key or config.provider == "ollama" else "✗ (需要 API Key)"
        print(f"  {key:20s} - {config.name:20s} [{config.provider}] {status}")

    print("\n使用 --models 参数指定要使用的模型")
    print("例如: python main.py --models gpt-3.5-turbo claude-3-haiku\n")


async def main():
    """主函数"""
    args = parse_args()

    # 列出模型
    if args.list_models:
        list_available_models()
        return

    # 确定要使用的模型
    model_keys = args.models if args.models else get_default_models()

    # 创建模型实例
    models = []
    for key in model_keys:
        model = create_model(key)
        if model:
            models.append(model)

    if not models:
        print_error("没有可用的模型！请检查 API Key 配置。")
        print_info("运行 'python main.py --list-models' 查看可用模型")
        sys.exit(1)

    # 运行
    if args.query:
        await single_query_mode(models, args.query)
    else:
        await interactive_mode(models)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_goodbye()
