"""旅行计划数据模型 —— 既给 FastAPI 做请求 / 响应，又给 StructuredLLM 做输出 schema"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ============ 请求 ============


class TripRequest(BaseModel):
    """旅行规划请求"""

    city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    travel_days: int = Field(..., ge=1, le=15, description="旅行天数")
    transportation: str = Field(default="公共交通", description="交通方式")
    accommodation: str = Field(default="经济型酒店", description="住宿偏好")
    preferences: List[str] = Field(default_factory=list, description="旅行偏好标签")
    free_text_input: str = Field(default="", description="额外要求")


# ============ 计划子结构 ============


class Location(BaseModel):
    longitude: float = Field(..., description="经度")
    latitude: float = Field(..., description="纬度")


class Attraction(BaseModel):
    name: str = Field(..., description="景点名称")
    address: str = Field(default="", description="地址")
    location: Optional[Location] = Field(default=None, description="经纬度")
    visit_duration: int = Field(default=120, description="建议游览时长（分钟）")
    description: str = Field(default="", description="景点描述")
    category: str = Field(default="景点", description="类别")
    ticket_price: int = Field(default=0, description="门票（元）")


class Meal(BaseModel):
    type: str = Field(..., description="breakfast/lunch/dinner")
    name: str = Field(..., description="餐厅或推荐名称")
    description: str = Field(default="", description="描述")
    estimated_cost: int = Field(default=0, description="预估费用（元）")


class Hotel(BaseModel):
    name: str = Field(..., description="酒店名")
    address: str = Field(default="", description="酒店地址")
    location: Optional[Location] = Field(default=None, description="酒店位置")
    price_range: str = Field(default="", description="价格区间")
    estimated_cost: int = Field(default=0, description="预估每晚（元）")


class WeatherInfo(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    day_weather: str = Field(default="", description="白天天气")
    night_weather: str = Field(default="", description="夜间天气")
    day_temp: int = Field(default=0, description="白天温度（℃）")
    night_temp: int = Field(default=0, description="夜间温度（℃）")
    wind: str = Field(default="", description="风向风力")


class DayPlan(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    day_index: int = Field(..., description="第几天，0 起步")
    description: str = Field(..., description="当日行程概述")
    transportation: str = Field(default="公共交通", description="交通方式")
    hotel: Optional[Hotel] = Field(default=None, description="推荐酒店")
    attractions: List[Attraction] = Field(default_factory=list, description="景点列表")
    meals: List[Meal] = Field(default_factory=list, description="餐饮列表")


class Budget(BaseModel):
    total_attractions: int = Field(default=0)
    total_hotels: int = Field(default=0)
    total_meals: int = Field(default=0)
    total_transportation: int = Field(default=0)
    total: int = Field(default=0)


class TripPlan(BaseModel):
    """整份旅行计划 —— 也是 with_structured_output 的目标 schema"""

    city: str = Field(..., description="城市")
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    days: List[DayPlan] = Field(..., description="每日行程")
    weather_info: List[WeatherInfo] = Field(default_factory=list, description="逐日天气")
    overall_suggestions: str = Field(default="", description="总体建议")
    budget: Optional[Budget] = Field(default=None, description="预算")


# ============ API 响应 ============


class TripPlanResponse(BaseModel):
    success: bool
    message: str = ""
    data: Optional[TripPlan] = None
