#!/usr/bin/env python3
"""
智能写作助手 - 主入口
基于 Gemini 的多模式写作助手

运行：python main.py
"""

import sys
from pathlib import Path

from writing_modes import WritingMode, WRITING_MODES
from prompts import BlogPrompt, EmailPrompt, CopywritingPrompt, CodeDocsPrompt
from llm import GeminiClient
from utils import Display


# 模式到 Prompt 类的映射
PROMPT_CLASSES = {
    WritingMode.BLOG: BlogPrompt,
    WritingMode.EMAIL: EmailPrompt,
    WritingMode.COPYWRITING: CopywritingPrompt,
    WritingMode.CODE_DOCS: CodeDocsPrompt,
}

# 输入提示语
INPUT_PROMPTS = {
    WritingMode.BLOG: "请输入博客主题",
    WritingMode.EMAIL: "请描述邮件场景",
    WritingMode.COPYWRITING: "请描述产品/服务",
    WritingMode.CODE_DOCS: "请描述代码/功能",
}


def select_mode() -> WritingMode:
    """选择写作模式"""
    options = [
        f"{config.emoji} {config.name} - {config.description}"
        for config in WRITING_MODES.values()
    ]

    choice = Display.menu(options, "选择写作模式")
    if choice == -1:
        return None

    return list(WritingMode)[choice]


def select_style(mode: WritingMode) -> str:
    """选择写作风格"""
    config = WRITING_MODES[mode]
    options = [f"{style.name} - {style.description}" for style in config.styles]

    choice = Display.menu(options, "选择风格")
    if choice == -1:
        return None

    return config.styles[choice].prompt_modifier


def generate_content(
    client: GeminiClient, mode: WritingMode, style: str, user_input: str
) -> str:
    """生成写作内容"""
    prompt_class = PROMPT_CLASSES[mode]
    prompt = prompt_class.build(user_input, style)

    # 流式生成
    content = Display.stream_output(client.generate_stream(prompt))
    return content


def save_content(content: str):
    """保存内容到文件"""
    if Display.save_prompt():
        filename = Display.get_filename()
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        Display.success(f"已保存到 {filepath}")


def main():
    """主函数"""
    Display.header()

    # 初始化 Gemini 客户端
    try:
        client = GeminiClient()
        Display.info("Gemini 连接成功")
    except Exception as e:
        Display.error(f"初始化失败: {e}")
        sys.exit(1)

    while True:
        # 1. 选择模式
        mode = select_mode()
        if mode is None:
            Display.info("感谢使用，再见！👋")
            break

        # 2. 选择风格
        style = select_style(mode)
        if style is None:
            continue

        # 3. 获取用户输入
        user_input = Display.input(INPUT_PROMPTS[mode])
        if not user_input.strip():
            Display.error("输入不能为空")
            continue

        # 4. 生成内容
        try:
            content = generate_content(client, mode, style, user_input)
        except Exception as e:
            Display.error(f"生成失败: {e}")
            continue

        # 5. 保存选项
        save_content(content)


if __name__ == "__main__":
    main()
