"""
工具函数模块
"""

import tiktoken


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """计算文本的 token 数量"""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def count_messages_tokens(messages: list, model: str = "gpt-4o-mini") -> int:
    """计算消息列表的 token 数量"""
    total = 0
    for msg in messages:
        # 每条消息有额外的格式 token
        total += 4  # <im_start>, role, \n, <im_end>
        total += count_tokens(msg.get("content", ""), model)
    total += 2  # <im_start>assistant
    return total


def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_timestamp(dt) -> str:
    """格式化时间戳"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")
