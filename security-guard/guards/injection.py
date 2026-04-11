"""
提示词注入检测模块
"""

import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class InjectionResult:
    """注入检测结果"""

    is_injection: bool
    confidence: float
    matched_patterns: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL


class InjectionGuard:
    """提示词注入检测器"""

    # 注入攻击模式
    INJECTION_PATTERNS = [
        # 指令覆盖
        (r"忽略(之前|上面|以上|所有)(的)?(指令|说明|规则)", "指令覆盖", 0.9),
        (r"ignore (previous|above|all) (instructions?|rules?)", "指令覆盖", 0.9),
        (r"disregard (previous|above|all)", "指令覆盖", 0.9),
        # 角色切换
        (r"你(现在)?是(一个)?", "角色切换", 0.5),
        (r"从现在开始.*(扮演|充当|作为)", "角色切换", 0.7),
        (r"pretend (to be|you are)", "角色切换", 0.7),
        (r"act as (a|an)?", "角色切换", 0.5),
        # 系统提示泄露
        (
            r"(告诉|显示|输出|打印)(我)?(你的)?(系统|初始)(提示|指令|prompt)",
            "系统提示泄露",
            0.95,
        ),
        (
            r"(what|show|print|display).*(system|initial).*(prompt|instruction)",
            "系统提示泄露",
            0.95,
        ),
        (r"repeat.*(system|initial).*(prompt|instruction)", "系统提示泄露", 0.95),
        # 分隔符注入
        (r"```\s*(system|assistant|user)", "分隔符注入", 0.8),
        (r"\[SYSTEM\]|\[INST\]|\[/INST\]", "分隔符注入", 0.85),
        (r"<\|(im_start|im_end|system|user|assistant)\|>", "分隔符注入", 0.9),
        # 指令标记
        (r"###\s*(instruction|system|user|assistant)", "指令标记", 0.8),
        (r"</?instruction>|</?system>", "指令标记", 0.85),
    ]

    def __init__(self):
        self.patterns = [
            (re.compile(p, re.IGNORECASE), name, conf)
            for p, name, conf in self.INJECTION_PATTERNS
        ]

    def check(self, text: str) -> InjectionResult:
        """检测提示词注入"""
        matched = []
        max_confidence = 0.0

        for pattern, name, confidence in self.patterns:
            if pattern.search(text):
                matched.append(name)
                max_confidence = max(max_confidence, confidence)

        # 确定风险等级
        if max_confidence >= 0.9:
            risk_level = "CRITICAL"
        elif max_confidence >= 0.7:
            risk_level = "HIGH"
        elif max_confidence >= 0.5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return InjectionResult(
            is_injection=len(matched) > 0 and max_confidence >= 0.7,
            confidence=max_confidence,
            matched_patterns=matched,
            risk_level=risk_level if matched else "NONE",
        )

    def get_safe_text(self, text: str) -> str:
        """移除可能的注入内容"""
        # 移除特殊标记
        safe = re.sub(r"<\|[^|]+\|>", "", text)
        safe = re.sub(r"\[/?[A-Z]+\]", "", safe)
        safe = re.sub(r"```\s*(system|assistant|user)\s*```", "", safe)
        return safe.strip()
