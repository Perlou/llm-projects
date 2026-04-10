"""
推理引擎模块
支持多种后端
"""

import torch
from typing import Generator, List, Optional
from abc import ABC, abstractmethod
import uuid

from app.config import settings
from app.models import Message


class BaseEngine(ABC):
    """推理引擎基类"""

    @abstractmethod
    def load(self):
        """加载模型"""
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> str:
        """生成回复"""
        pass

    @abstractmethod
    def stream_generate(
        self,
        messages: List[Message],
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> Generator[str, None, None]:
        """流式生成"""
        pass


class TransformersEngine(BaseEngine):
    """Transformers 推理引擎"""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None

    def load(self):
        """加载模型"""
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_name = settings.model_path or settings.model_name

        print(f"正在加载模型: {model_name}")

        # 加载 tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 量化配置
        quantization_config = None
        if settings.load_in_4bit or settings.load_in_8bit:
            from transformers import BitsAndBytesConfig

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=settings.load_in_4bit,
                load_in_8bit=settings.load_in_8bit,
            )

        # 加载模型
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=settings.device_map,
            torch_dtype=torch.float16,
            quantization_config=quantization_config,
            trust_remote_code=True,
        )

        self.device = next(self.model.parameters()).device
        print(f"模型加载完成，设备: {self.device}")

    def _format_messages(self, messages: List[Message]) -> str:
        """格式化消息"""
        text = ""
        for msg in messages:
            if msg.role == "system":
                text += f"<|im_start|>system\n{msg.content}<|im_end|>\n"
            elif msg.role == "user":
                text += f"<|im_start|>user\n{msg.content}<|im_end|>\n"
            elif msg.role == "assistant":
                text += f"<|im_start|>assistant\n{msg.content}<|im_end|>\n"
        text += "<|im_start|>assistant\n"
        return text

    def generate(
        self,
        messages: List[Message],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """生成回复"""
        prompt = self._format_messages(messages)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1] :],
            skip_special_tokens=True,
        )

        # 清理结束标记
        if "<|im_end|>" in response:
            response = response.split("<|im_end|>")[0]

        return response.strip()

    def stream_generate(
        self,
        messages: List[Message],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> Generator[str, None, None]:
        """流式生成"""
        from transformers import TextIteratorStreamer
        from threading import Thread

        prompt = self._format_messages(messages)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        generation_kwargs = {
            **inputs,
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": temperature > 0,
            "streamer": streamer,
            "pad_token_id": self.tokenizer.pad_token_id,
        }

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        for text in streamer:
            if "<|im_end|>" in text:
                text = text.split("<|im_end|>")[0]
                if text:
                    yield text
                break
            yield text

        thread.join()

    def count_tokens(self, text: str) -> int:
        """计算 token 数量"""
        return len(self.tokenizer.encode(text))


def create_engine() -> BaseEngine:
    """创建推理引擎"""
    engine_type = settings.inference_engine.lower()

    if engine_type == "transformers":
        return TransformersEngine()
    else:
        raise ValueError(f"不支持的推理引擎: {engine_type}")


# 全局引擎实例
_engine: Optional[BaseEngine] = None


def get_engine() -> BaseEngine:
    """获取引擎实例"""
    global _engine
    if _engine is None:
        _engine = create_engine()
        _engine.load()
    return _engine
