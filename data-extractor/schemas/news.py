"""
新闻事件数据模型
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Entity(BaseModel):
    """实体"""

    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型（人物/组织/地点）")
    role: Optional[str] = Field(default=None, description="在事件中的角色")


class NewsEvent(BaseModel):
    """新闻事件"""

    title: str = Field(description="事件标题/摘要")
    event_type: str = Field(description="事件类型（如：政治、经济、科技、体育）")
    date: Optional[str] = Field(default=None, description="事件发生日期")
    location: Optional[str] = Field(default=None, description="事件发生地点")
    entities: List[Entity] = Field(default_factory=list, description="涉及的实体")
    summary: str = Field(description="事件摘要（2-3句话）")
    impact: Optional[str] = Field(default=None, description="事件影响")
