"""
合同信息数据模型
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Party(BaseModel):
    """合同方"""

    name: str = Field(description="名称")
    role: str = Field(description="角色（甲方/乙方/丙方）")
    representative: Optional[str] = Field(default=None, description="法定代表人")


class ContractInfo(BaseModel):
    """合同信息"""

    title: str = Field(description="合同标题")
    contract_type: str = Field(description="合同类型（如：采购合同、租赁合同）")
    parties: List[Party] = Field(description="合同各方")
    effective_date: Optional[str] = Field(default=None, description="生效日期")
    expiry_date: Optional[str] = Field(default=None, description="到期日期")
    amount: Optional[str] = Field(default=None, description="合同金额")
    payment_terms: Optional[str] = Field(default=None, description="付款条款")
    key_terms: List[str] = Field(default_factory=list, description="关键条款摘要")
    penalties: Optional[str] = Field(default=None, description="违约责任")
