"""
简历信息数据模型
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Education(BaseModel):
    """教育经历"""

    school: str = Field(description="学校名称")
    major: Optional[str] = Field(default=None, description="专业")
    degree: Optional[str] = Field(default=None, description="学位（本科/硕士/博士）")
    graduation_year: Optional[int] = Field(default=None, description="毕业年份")


class WorkExperience(BaseModel):
    """工作经历"""

    company: str = Field(description="公司名称")
    position: str = Field(description="职位")
    start_year: int = Field(description="开始年份")
    end_year: Optional[int] = Field(default=None, description="结束年份，null表示至今")
    description: Optional[str] = Field(default=None, description="工作描述")


class ResumeInfo(BaseModel):
    """简历信息"""

    name: str = Field(description="姓名")
    gender: Optional[str] = Field(default=None, description="性别")
    birth_date: Optional[str] = Field(
        default=None, description="出生日期（格式：YYYY-MM）"
    )
    phone: Optional[str] = Field(default=None, description="电话号码")
    email: Optional[str] = Field(default=None, description="电子邮箱")
    location: Optional[str] = Field(default=None, description="所在地")
    education: List[Education] = Field(default_factory=list, description="教育经历列表")
    work_experience: List[WorkExperience] = Field(
        default_factory=list, description="工作经历列表"
    )
    skills: List[str] = Field(default_factory=list, description="技能列表")
