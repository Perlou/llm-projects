"""
数据集工具模块
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class DataSample:
    """数据样本"""

    instruction: str
    input: str = ""
    output: str = ""


def load_json(file_path: str) -> List[Dict]:
    """加载 JSON 数据"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: List[Dict], file_path: str):
    """保存 JSON 数据"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def convert_alpaca_to_messages(sample: Dict) -> Dict:
    """将 Alpaca 格式转换为消息格式"""
    instruction = sample.get("instruction", "")
    input_text = sample.get("input", "")
    output = sample.get("output", "")

    # 构建用户消息
    if input_text:
        user_content = f"{instruction}\n\n{input_text}"
    else:
        user_content = instruction

    return {
        "messages": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": output},
        ]
    }


def convert_sharegpt_to_messages(sample: Dict) -> Dict:
    """将 ShareGPT 格式转换为消息格式"""
    messages = []

    for conv in sample.get("conversations", []):
        role_map = {"human": "user", "gpt": "assistant", "system": "system"}
        role = role_map.get(conv.get("from", ""), "user")
        content = conv.get("value", "")
        messages.append({"role": role, "content": content})

    return {"messages": messages}


def validate_sample(sample: Dict, format_type: str) -> bool:
    """验证数据样本"""
    if format_type == "alpaca":
        return bool(sample.get("instruction") and sample.get("output"))
    elif format_type == "sharegpt":
        convs = sample.get("conversations", [])
        return len(convs) >= 2
    elif format_type == "messages":
        msgs = sample.get("messages", [])
        return len(msgs) >= 2
    return False


def format_prompt(sample: Dict, format_type: str = "alpaca") -> str:
    """格式化提示词（用于预览）"""
    if format_type == "alpaca":
        instruction = sample.get("instruction", "")
        input_text = sample.get("input", "")
        output = sample.get("output", "")

        prompt = f"### 指令:\n{instruction}\n"
        if input_text:
            prompt += f"\n### 输入:\n{input_text}\n"
        prompt += f"\n### 回答:\n{output}"
        return prompt
    elif format_type == "sharegpt":
        conversations = sample.get("conversations", [])
        lines = []
        for conv in conversations:
            role = conv.get("from", "human")
            content = conv.get("value", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
    else:
        messages = sample.get("messages", [])
        lines = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)


def split_dataset(
    data: List[Dict], train_ratio: float = 0.9, shuffle: bool = True, seed: int = 42
) -> tuple:
    """分割数据集"""
    import random

    if not data:
        return [], []

    if shuffle:
        random.seed(seed)
        data = data.copy()
        random.shuffle(data)

    train_ratio = max(0.0, min(1.0, train_ratio))
    split_idx = int(len(data) * train_ratio)
    if len(data) == 1:
        split_idx = 1
    else:
        split_idx = min(max(split_idx, 1), len(data) - 1)

    return data[:split_idx], data[split_idx:]


def get_dataset_stats(data: List[Dict], format_type: str = "alpaca") -> Dict:
    """获取数据集统计信息"""
    stats = {
        "total_samples": len(data),
        "valid_samples": 0,
        "avg_instruction_len": 0,
        "avg_output_len": 0,
    }

    instruction_lens = []
    output_lens = []

    for sample in data:
        if validate_sample(sample, format_type):
            stats["valid_samples"] += 1

            if format_type == "alpaca":
                instruction_lens.append(len(sample.get("instruction", "")))
                output_lens.append(len(sample.get("output", "")))
            elif format_type == "sharegpt":
                convs = sample.get("conversations", [])
                for conv in convs:
                    role = conv.get("from")
                    content = conv.get("value", "")
                    if role == "human":
                        instruction_lens.append(len(content))
                    elif role == "gpt":
                        output_lens.append(len(content))
            elif format_type == "messages":
                msgs = sample.get("messages", [])
                for msg in msgs:
                    if msg.get("role") == "user":
                        instruction_lens.append(len(msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        output_lens.append(len(msg.get("content", "")))

    if instruction_lens:
        stats["avg_instruction_len"] = sum(instruction_lens) // len(instruction_lens)
    if output_lens:
        stats["avg_output_len"] = sum(output_lens) // len(output_lens)

    return stats
