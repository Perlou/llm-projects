"""
评论分析数据模型
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Aspect(BaseModel):
    """方面（维度）"""

    name: str = Field(description="方面名称（如：价格、质量、服务）")
    sentiment: str = Field(description="情感倾向（positive/negative/neutral）")
    mention: Optional[str] = Field(default=None, description="相关原文摘录")


class ReviewAnalysis(BaseModel):
    """评论分析结果"""

    overall_sentiment: str = Field(description="整体情感（positive/negative/neutral）")
    sentiment_score: float = Field(description="情感得分（-1到1，负为负面，正为正面）")
    aspects: List[Aspect] = Field(default_factory=list, description="各方面的情感分析")
    key_points: List[str] = Field(default_factory=list, description="评论要点")
    recommendation: Optional[str] = Field(
        default=None, description="是否推荐（yes/no/unclear）"
    )
    summary: str = Field(description="评论一句话总结")
