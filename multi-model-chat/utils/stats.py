"""
统计工具
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResponseStats:
    """响应统计"""

    model: str
    provider: str

    # 内容
    content: str = ""
    error: Optional[str] = None

    # Token 统计
    input_tokens: int = 0
    output_tokens: int = 0

    # 时间统计（秒）
    first_token_time: float = 0.0
    total_time: float = 0.0

    # 成本（美元）
    cost: float = 0.0

    @property
    def tokens_per_second(self) -> float:
        """生成速度（tokens/s）"""
        if self.total_time > 0 and self.output_tokens > 0:
            return self.output_tokens / self.total_time
        return 0.0

    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.error is None


def format_cost(cost: float) -> str:
    """格式化成本显示"""
    if cost == 0:
        return "免费"
    elif cost < 0.01:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"


def format_time(seconds: float) -> str:
    """格式化时间显示"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    else:
        return f"{seconds:.2f}s"


def format_tokens(tokens: int) -> str:
    """格式化 token 数显示"""
    if tokens >= 1000:
        return f"{tokens / 1000:.1f}K"
    return str(tokens)
