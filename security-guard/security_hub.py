"""
安全检查中心
整合所有安全检查模块
"""

from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from config import config
from guards.injection import InjectionGuard, InjectionResult
from guards.jailbreak import JailbreakGuard, JailbreakResult
from guards.pii_filter import PIIFilter, PIIResult
from guards.content_filter import ContentFilter, ContentCheckResult
from guards.rules_engine import RulesEngine, RulesResult


@dataclass
class SecurityCheckResult:
    """综合安全检查结果"""

    is_safe: bool
    risk_level: str  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    risks: List[str]

    # 各模块结果
    injection: Optional[InjectionResult] = None
    jailbreak: Optional[JailbreakResult] = None
    pii: Optional[PIIResult] = None
    content: Optional[ContentCheckResult] = None
    rules: Optional[RulesResult] = None

    # 过滤后的文本
    filtered_text: Optional[str] = None

    # 时间戳
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SecurityHub:
    """安全检查中心"""

    def __init__(self):
        # 初始化各检查模块
        self.injection_guard = (
            InjectionGuard() if config.enable_injection_check else None
        )
        self.jailbreak_guard = (
            JailbreakGuard() if config.enable_jailbreak_check else None
        )
        self.pii_filter = PIIFilter() if config.enable_pii_filter else None
        self.content_filter = ContentFilter() if config.enable_content_filter else None
        self.rules_engine = RulesEngine()

    def check_input(self, text: str) -> SecurityCheckResult:
        """检查用户输入"""
        risks = []
        risk_levels = []
        filtered_text = text

        # 注入检测
        injection_result = None
        if self.injection_guard:
            injection_result = self.injection_guard.check(text)
            if injection_result.is_injection:
                risks.append(
                    f"注入攻击: {', '.join(injection_result.matched_patterns)}"
                )
                risk_levels.append(injection_result.risk_level)

        # 越狱检测
        jailbreak_result = None
        if self.jailbreak_guard:
            jailbreak_result = self.jailbreak_guard.check(text)
            if jailbreak_result.is_jailbreak:
                risks.append(f"越狱攻击: {jailbreak_result.attack_type}")
                risk_levels.append(
                    "HIGH" if jailbreak_result.confidence > 0.8 else "MEDIUM"
                )

        # PII 过滤
        pii_result = None
        if self.pii_filter:
            pii_result = self.pii_filter.filter(text)
            if pii_result.has_pii:
                filtered_text = pii_result.filtered_text
                pii_types = [m.pii_type for m in pii_result.matches]
                risks.append(f"敏感信息: {', '.join(set(pii_types))}")

        # 规则检查
        rules_result = self.rules_engine.check(text)
        if rules_result.is_blocked:
            blocked_rules = [m.rule.name for m in rules_result.matches]
            risks.append(f"规则拦截: {', '.join(blocked_rules)}")
            risk_levels.append("CRITICAL")

        # 确定总体风险等级
        risk_level = self._determine_risk_level(risk_levels)
        is_safe = risk_level in ["NONE", "LOW"]

        return SecurityCheckResult(
            is_safe=is_safe,
            risk_level=risk_level,
            risks=risks,
            injection=injection_result,
            jailbreak=jailbreak_result,
            pii=pii_result,
            rules=rules_result,
            filtered_text=filtered_text if filtered_text != text else None,
        )

    def check_output(self, text: str) -> SecurityCheckResult:
        """检查模型输出"""
        risks = []
        risk_levels = []
        filtered_text = text

        # 内容过滤
        content_result = None
        if self.content_filter:
            content_result = self.content_filter.check(text)
            if not content_result.is_safe:
                risks.append(
                    f"内容违规: {', '.join(content_result.flagged_categories)}"
                )
                risk_levels.append(
                    "HIGH" if content_result.confidence > 0.8 else "MEDIUM"
                )

        # PII 过滤
        pii_result = None
        if self.pii_filter:
            pii_result = self.pii_filter.filter(text)
            if pii_result.has_pii:
                filtered_text = pii_result.filtered_text
                risks.append("输出包含敏感信息")

        risk_level = self._determine_risk_level(risk_levels)
        is_safe = risk_level in ["NONE", "LOW"]

        return SecurityCheckResult(
            is_safe=is_safe,
            risk_level=risk_level,
            risks=risks,
            content=content_result,
            pii=pii_result,
            filtered_text=filtered_text if filtered_text != text else None,
        )

    def filter_pii(self, text: str) -> str:
        """过滤敏感信息"""
        if self.pii_filter:
            result = self.pii_filter.filter(text)
            return result.filtered_text
        return text

    def add_rule(
        self, name: str, pattern: str, action: str = "warn", message: str = ""
    ):
        """添加自定义规则"""
        self.rules_engine.add_rule_from_dict(name, pattern, action, message)

    def _determine_risk_level(self, levels: List[str]) -> str:
        """确定总体风险等级"""
        if not levels:
            return "NONE"

        priority = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
        max_level = max(levels, key=lambda x: priority.get(x, 0))
        return max_level

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "injection_enabled": self.injection_guard is not None,
            "jailbreak_enabled": self.jailbreak_guard is not None,
            "pii_enabled": self.pii_filter is not None,
            "content_filter_enabled": self.content_filter is not None,
            "rules_count": len(self.rules_engine.get_rules()),
        }
