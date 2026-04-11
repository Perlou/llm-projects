"""
规则引擎模块
"""

import re
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum


class RuleAction(Enum):
    """规则动作"""

    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"
    FILTER = "filter"


@dataclass
class Rule:
    """安全规则"""

    name: str
    pattern: str
    action: RuleAction
    message: str
    priority: int = 0
    enabled: bool = True
    _compiled: Any = field(default=None, repr=False)

    def __post_init__(self):
        self._compiled = re.compile(self.pattern, re.IGNORECASE)

    def match(self, text: str) -> bool:
        """匹配规则"""
        return bool(self._compiled.search(text))


@dataclass
class RuleMatch:
    """规则匹配结果"""

    rule: Rule
    matched_text: str


@dataclass
class RulesResult:
    """规则引擎结果"""

    is_blocked: bool
    matches: List[RuleMatch]
    warnings: List[str]
    filtered_text: Optional[str]


class RulesEngine:
    """规则引擎"""

    def __init__(self):
        self.rules: List[Rule] = []
        self._load_default_rules()

    def _load_default_rules(self):
        """加载默认规则"""
        default_rules = [
            Rule(
                name="system_prompt_leak",
                pattern=r"(system|初始)(prompt|提示词)",
                action=RuleAction.BLOCK,
                message="禁止尝试获取系统提示词",
                priority=100,
            ),
            Rule(
                name="code_injection",
                pattern=r"(exec|eval|os\.system|subprocess)",
                action=RuleAction.WARN,
                message="检测到可能的代码注入",
                priority=90,
            ),
            Rule(
                name="sql_injection",
                pattern=r"(drop\s+table|delete\s+from|union\s+select)",
                action=RuleAction.BLOCK,
                message="检测到 SQL 注入",
                priority=95,
            ),
        ]

        for rule in default_rules:
            self.add_rule(rule)

    def add_rule(self, rule: Rule):
        """添加规则"""
        self.rules.append(rule)
        # 按优先级排序
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def add_rule_from_dict(
        self,
        name: str,
        pattern: str,
        action: str = "warn",
        message: str = "",
        priority: int = 0,
    ):
        """从字典添加规则"""
        rule = Rule(
            name=name,
            pattern=pattern,
            action=RuleAction(action),
            message=message or f"匹配规则: {name}",
            priority=priority,
        )
        self.add_rule(rule)

    def remove_rule(self, name: str):
        """移除规则"""
        self.rules = [r for r in self.rules if r.name != name]

    def enable_rule(self, name: str, enabled: bool = True):
        """启用/禁用规则"""
        for rule in self.rules:
            if rule.name == name:
                rule.enabled = enabled
                break

    def check(self, text: str) -> RulesResult:
        """检查文本"""
        matches = []
        warnings = []
        is_blocked = False
        filtered_text = text

        for rule in self.rules:
            if not rule.enabled:
                continue

            if rule.match(text):
                match = rule._compiled.search(text)
                matches.append(
                    RuleMatch(
                        rule=rule,
                        matched_text=match.group() if match else "",
                    )
                )

                if rule.action == RuleAction.BLOCK:
                    is_blocked = True
                elif rule.action == RuleAction.WARN:
                    warnings.append(rule.message)
                elif rule.action == RuleAction.FILTER:
                    # 过滤匹配内容
                    filtered_text = rule._compiled.sub("[FILTERED]", filtered_text)

        return RulesResult(
            is_blocked=is_blocked,
            matches=matches,
            warnings=warnings,
            filtered_text=filtered_text if filtered_text != text else None,
        )

    def get_rules(self) -> List[Rule]:
        """获取所有规则"""
        return self.rules.copy()

    def export_rules(self) -> List[Dict]:
        """导出规则"""
        return [
            {
                "name": r.name,
                "pattern": r.pattern,
                "action": r.action.value,
                "message": r.message,
                "priority": r.priority,
                "enabled": r.enabled,
            }
            for r in self.rules
        ]
