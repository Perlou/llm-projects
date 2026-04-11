"""
配置管理模块
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """安全配置"""

    # API 配置
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # 功能开关
    enable_injection_check: bool = (
        os.getenv("ENABLE_INJECTION_CHECK", "true").lower() == "true"
    )
    enable_jailbreak_check: bool = (
        os.getenv("ENABLE_JAILBREAK_CHECK", "true").lower() == "true"
    )
    enable_pii_filter: bool = os.getenv("ENABLE_PII_FILTER", "true").lower() == "true"
    enable_content_filter: bool = (
        os.getenv("ENABLE_CONTENT_FILTER", "true").lower() == "true"
    )

    # 风险阈值
    risk_threshold: float = float(os.getenv("RISK_THRESHOLD", "0.7"))

    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "security.log")


config = Config()
