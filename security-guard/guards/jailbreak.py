"""
越狱攻击防护模块
"""

import re
from typing import List
from dataclasses import dataclass


@dataclass
class JailbreakResult:
    """越狱检测结果"""

    is_jailbreak: bool
    confidence: float
    attack_type: str
    details: str


class JailbreakGuard:
    """越狱攻击检测器"""

    # 越狱攻击模式
    JAILBREAK_PATTERNS = {
        "DAN": [
            r"DAN\s*(mode|模式)?",
            r"Developer\s*Mode",
            r"Do\s*Anything\s*Now",
            r"无限制模式",
        ],
        "角色扮演绕过": [
            r"假装你没有(任何)?限制",
            r"你是一个没有道德(约束)?的",
            r"作为一个邪恶的",
            r"pretend you have no (restrictions|limits)",
            r"you are an evil",
            r"无视(所有)?安全(规则|限制)",
        ],
        "编码绕过": [
            r"用(base64|hex|二进制)编码回答",
            r"respond in (base64|hexadecimal|binary)",
            r"使用(隐语|暗语|密码)回答",
        ],
        "假设场景": [
            r"假设你是.*没有(限制|规则)",
            r"在一个(虚构|假想)的世界(里|中)",
            r"如果你可以做任何事",
            r"hypothetically.*(no (rules|restrictions))",
            r"in a fictional world",
        ],
        "情感操纵": [
            r"我(会|要)(死|自杀).*(如果你不|除非)",
            r"我的生命(取决于|依赖)",
            r"这是紧急情况.*(必须|一定要)",
            r"(my life depends|I will die).*(if you don't|unless)",
        ],
    }

    def __init__(self):
        self.patterns = {}
        for attack_type, patterns in self.JAILBREAK_PATTERNS.items():
            self.patterns[attack_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def check(self, text: str) -> JailbreakResult:
        """检测越狱攻击"""
        for attack_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    # 根据攻击类型确定置信度
                    confidence = self._get_confidence(attack_type)

                    return JailbreakResult(
                        is_jailbreak=True,
                        confidence=confidence,
                        attack_type=attack_type,
                        details=f"匹配: {match.group()}",
                    )

        return JailbreakResult(
            is_jailbreak=False,
            confidence=0.0,
            attack_type="",
            details="未检测到越狱攻击",
        )

    def _get_confidence(self, attack_type: str) -> float:
        """根据攻击类型返回置信度"""
        confidence_map = {
            "DAN": 0.95,
            "角色扮演绕过": 0.85,
            "编码绕过": 0.8,
            "假设场景": 0.75,
            "情感操纵": 0.9,
        }
        return confidence_map.get(attack_type, 0.7)

    def get_attack_types(self) -> List[str]:
        """获取所有攻击类型"""
        return list(self.patterns.keys())
