"""
模型工具模块
"""

import os
from typing import Optional, Dict, Any
import torch


def _resolve_torch_dtype():
    """根据设备选择合适的数据类型。"""
    return torch.float16 if torch.cuda.is_available() else torch.float32


def load_base_model(
    model_name: str,
    quantization_config=None,
    trust_remote_code: bool = True,
    device_map: str = "auto",
):
    """加载基础模型"""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"正在加载模型: {model_name}")

    # 加载 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=trust_remote_code,
    )

    # 设置 padding
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # 加载模型
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map=device_map,
        trust_remote_code=trust_remote_code,
        torch_dtype=_resolve_torch_dtype(),
    )

    print(f"模型加载完成，参数量: {model.num_parameters():,}")

    return model, tokenizer


def apply_lora(model, lora_config):
    """应用 LoRA"""
    from peft import get_peft_model

    model = get_peft_model(model, lora_config)

    # 统计可训练参数
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    all_params = sum(p.numel() for p in model.parameters())

    print(
        f"可训练参数: {trainable_params:,} ({100 * trainable_params / all_params:.2f}%)"
    )

    return model


def merge_lora_weights(
    base_model_name: str,
    adapter_path: str,
    output_path: str,
    trust_remote_code: bool = True,
):
    """合并 LoRA 权重到基础模型"""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    print(f"加载基础模型: {base_model_name}")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=_resolve_torch_dtype(),
        device_map="auto",
        trust_remote_code=trust_remote_code,
    )

    print(f"加载 LoRA 适配器: {adapter_path}")
    model = PeftModel.from_pretrained(base_model, adapter_path)

    print("合并权重...")
    model = model.merge_and_unload()

    print(f"保存合并后的模型到: {output_path}")
    os.makedirs(output_path, exist_ok=True)
    model.save_pretrained(output_path)

    # 复制 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        base_model_name,
        trust_remote_code=trust_remote_code,
    )
    tokenizer.save_pretrained(output_path)

    print("模型合并完成！")
    return output_path


def generate_response(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
    do_sample: bool = True,
) -> str:
    """生成响应"""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_length = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=do_sample,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generated_ids = outputs[0][input_length:]
    response = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

    return response


def get_model_info(model) -> Dict[str, Any]:
    """获取模型信息"""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    return {
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "trainable_percentage": 100 * trainable_params / total_params,
        "dtype": str(next(model.parameters()).dtype),
        "device": str(next(model.parameters()).device),
    }
