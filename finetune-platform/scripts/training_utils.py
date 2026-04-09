"""
训练工具模块
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class LoRAConfig:
    """LoRA 配置"""

    r: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: list = field(
        default_factory=lambda: [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
    )


@dataclass
class TrainingConfig:
    """训练配置"""

    output_dir: str = "./outputs"
    num_epochs: int = 3
    per_device_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"
    max_seq_length: int = 1024
    logging_steps: int = 10
    save_steps: int = 100
    save_total_limit: int = 3
    fp16: bool = True
    gradient_checkpointing: bool = True
    optim: str = "paged_adamw_32bit"


@dataclass
class QuantizationConfig:
    """量化配置"""

    enabled: bool = False
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True


def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_peft_config(lora_cfg: Dict) -> Dict:
    """获取 PEFT 配置"""
    from peft import LoraConfig, TaskType

    return LoraConfig(
        r=lora_cfg.get("r", 16),
        lora_alpha=lora_cfg.get("alpha", 32),
        lora_dropout=lora_cfg.get("dropout", 0.05),
        target_modules=lora_cfg.get(
            "target_modules", ["q_proj", "k_proj", "v_proj", "o_proj"]
        ),
        task_type=TaskType.CAUSAL_LM,
        bias="none",
    )


def get_quantization_config(quant_cfg: Dict):
    """获取量化配置"""
    if not quant_cfg.get("enabled", False):
        return None

    from transformers import BitsAndBytesConfig
    import torch

    compute_dtype = getattr(torch, quant_cfg.get("bnb_4bit_compute_dtype", "float16"))

    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_quant_type=quant_cfg.get("bnb_4bit_quant_type", "nf4"),
        bnb_4bit_use_double_quant=quant_cfg.get("bnb_4bit_use_double_quant", True),
    )


def get_training_arguments(
    training_cfg: Dict,
    output_dir: str = None,
    evaluation_cfg: Dict = None,
    has_eval_dataset: bool = True,
):
    """获取训练参数"""
    from transformers import TrainingArguments

    evaluation_cfg = evaluation_cfg or {}
    do_eval = bool(evaluation_cfg.get("do_eval", True) and has_eval_dataset)
    eval_steps = evaluation_cfg.get(
        "eval_steps", max(1, int(training_cfg.get("logging_steps", 10)))
    )
    metric_for_best_model = evaluation_cfg.get("metric_for_best_model", "eval_loss")
    greater_is_better = False if "loss" in metric_for_best_model else None

    return TrainingArguments(
        output_dir=output_dir or training_cfg.get("output_dir", "./outputs"),
        num_train_epochs=training_cfg.get("num_epochs", 3),
        per_device_train_batch_size=training_cfg.get("per_device_batch_size", 4),
        per_device_eval_batch_size=training_cfg.get("per_device_batch_size", 4),
        gradient_accumulation_steps=training_cfg.get("gradient_accumulation_steps", 4),
        learning_rate=training_cfg.get("learning_rate", 2e-4),
        weight_decay=training_cfg.get("weight_decay", 0.01),
        warmup_ratio=training_cfg.get("warmup_ratio", 0.03),
        lr_scheduler_type=training_cfg.get("lr_scheduler_type", "cosine"),
        logging_steps=training_cfg.get("logging_steps", 10),
        save_steps=training_cfg.get("save_steps", 100),
        save_total_limit=training_cfg.get("save_total_limit", 3),
        fp16=training_cfg.get("fp16", True),
        gradient_checkpointing=training_cfg.get("gradient_checkpointing", True),
        optim=training_cfg.get("optim", "paged_adamw_32bit"),
        report_to="none",
        remove_unused_columns=False,
        do_eval=do_eval,
        evaluation_strategy="steps" if do_eval else "no",
        eval_steps=eval_steps if do_eval else None,
        metric_for_best_model=metric_for_best_model if do_eval else None,
        load_best_model_at_end=do_eval,
        greater_is_better=greater_is_better if do_eval else None,
    )


class TrainingLogger:
    """训练日志记录器"""

    def __init__(self, log_file: str = None):
        self.log_file = log_file
        self.logs = []

    def log(self, step: int, loss: float, lr: float, **kwargs):
        """记录训练步骤"""
        entry = {"step": step, "loss": loss, "learning_rate": lr, **kwargs}
        self.logs.append(entry)

        # 打印日志
        print(f"Step {step} | Loss: {loss:.4f} | LR: {lr:.2e}")

        # 写入文件
        if self.log_file:
            import json

            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def get_summary(self) -> Dict:
        """获取训练摘要"""
        if not self.logs:
            return {}

        losses = [log["loss"] for log in self.logs]
        return {
            "total_steps": len(self.logs),
            "final_loss": losses[-1],
            "min_loss": min(losses),
            "avg_loss": sum(losses) / len(losses),
        }
