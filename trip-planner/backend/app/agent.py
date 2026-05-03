"""旅行规划 Agent —— ClearAgent 三件套：MCPClient + ReActAgent + StructuredLLM

核心流程：

1. ``MCPClient.connect_stdio`` 起一个 ``uvx amap-mcp-server`` 子进程
2. ``client.register_to(registry)`` 把 ``maps_text_search`` / ``maps_weather`` 等
   工具一次性灌进 ClearAgent 的 ``ToolRegistry``
3. ``ReActAgent`` 自动多轮 Function Calling 调上面这些 MCP 工具
   收集景点 / 天气 / 酒店素材
4. ``llm.with_structured_output(TripPlan)`` 把 agent 文本输出 + 原始请求
   喂给 LLM，直出 Pydantic ``TripPlan`` 实例（无需手工解析 JSON）
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from clear_agent.agents.react_agent import ReActAgent
from clear_agent.core.llm import ClearAgentLLM
from clear_agent.mcp.client import MCPClient
from clear_agent.tools.registry import ToolRegistry

from .config import get_settings
from .schemas import (
    Attraction,
    DayPlan,
    Meal,
    TripPlan,
    TripRequest,
)

logger = logging.getLogger(__name__)


# ============ 提示词 ============

SYSTEM_PROMPT = """你是一个专业的旅行规划助手。

## 工作要求
你必须**主动调用高德地图 MCP 工具**收集真实数据，而不是凭空想象。可用工具示例：
- `maps_text_search(keywords, city)` —— 搜索景点 / 酒店 / 餐厅 POI
- `maps_weather(city)` —— 查询城市天气

## 推荐流程
1. 用 `Thought` 工具简要梳理需求
2. 调 `maps_text_search` 搜目标城市的核心景点（按用户偏好关键词）
3. 调 `maps_weather` 查目的地天气
4. 调 `maps_text_search` 搜推荐酒店类型
5. 信息齐全后用 `Finish` 把所有原始信息（景点列表、天气、酒店候选）整理成结构化文本返回

## 重要
- 必须真实调用工具拿数据，不要编造经纬度、天气、价格
- 收集到的 POI 信息（名字、地址、经纬度）请完整保留，后续会用来生成最终行程
"""


PLANNER_PROMPT = """你是一个旅行规划专家。基于下面收集到的真实素材，为用户生成一份完整的多日旅行计划。

## 用户原始需求
- 城市：{city}
- 日期：{start_date} 至 {end_date}（共 {days} 天）
- 交通偏好：{transportation}
- 住宿偏好：{accommodation}
- 风格偏好：{preferences}
- 额外要求：{free_text_input}

## 素材（来自高德 MCP 工具的真实输出）
{material}

## 输出要求
1. 每天安排 2~3 个景点，按地理位置就近成组，避免来回跑
2. 每天必须包含早 / 中 / 晚三餐推荐
3. 每天推荐 1 家具体酒店（从素材中挑选，复用真实地址 / 经纬度）
4. weather_info 数组对应每一天的天气；day_temp / night_temp 必须是纯数字（℃，不带单位）
5. budget 给出各项小计 + 总计，单位元
6. overall_suggestions 写实用的旅行 Tip
7. day_index 从 0 开始递增

直接返回符合 schema 的对象，无需任何额外文字解释。
"""


# ============ 单例 Planner ============


class TripPlannerService:
    """全局只创建一次，复用 LLM / MCP / Agent"""

    def __init__(self) -> None:
        settings = get_settings()
        settings.assert_ready()

        logger.info("初始化 ClearAgent LLM ...")
        self.llm = ClearAgentLLM(
            model=settings.llm_model_id,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
        )

        logger.info("启动高德 MCP server (uvx amap-mcp-server) ...")
        self.registry = ToolRegistry()
        self.mcp_client = MCPClient.connect_stdio(
            command="uvx",
            args=["amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY": settings.amap_maps_api_key},
        )
        n = self.mcp_client.register_to(self.registry)
        logger.info("已从 MCP 注册 %d 个工具", n)

        logger.info("创建 ReActAgent ...")
        self.agent = ReActAgent(
            name="旅行规划助手",
            llm=self.llm,
            tool_registry=self.registry,
            system_prompt=SYSTEM_PROMPT,
            max_steps=10,
        )

        # 结构化输出器（懒构造一次）
        self.structured_llm = self.llm.with_structured_output(TripPlan)

    # ---------------------------------------------------------- public

    def plan(self, request: TripRequest) -> TripPlan:
        """主入口：调用 ReAct agent 收集素材 → 结构化生成 TripPlan"""
        logger.info("开始规划 %s %d 天", request.city, request.travel_days)

        # 1) ReAct 收集素材
        gathering_query = self._build_gathering_query(request)
        try:
            material = self.agent.run(gathering_query)
        except Exception as exc:  # noqa: BLE001
            logger.exception("ReAct 阶段失败: %s", exc)
            material = ""

        if not material or len(material) < 30:
            logger.warning("素材为空 / 过短，使用 fallback 计划")
            return self._fallback_plan(request)

        # 2) 结构化输出 TripPlan
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个旅行规划专家，请严格按 schema 输出 JSON。",
                },
                {
                    "role": "user",
                    "content": PLANNER_PROMPT.format(
                        city=request.city,
                        start_date=request.start_date,
                        end_date=request.end_date,
                        days=request.travel_days,
                        transportation=request.transportation,
                        accommodation=request.accommodation,
                        preferences=", ".join(request.preferences) or "无",
                        free_text_input=request.free_text_input or "无",
                        material=material,
                    ),
                },
            ]
            plan = self.structured_llm.invoke(messages)
            assert isinstance(plan, TripPlan)
            return plan
        except Exception as exc:  # noqa: BLE001
            logger.exception("结构化输出失败: %s", exc)
            return self._fallback_plan(request)

    # ---------------------------------------------------------- helpers

    def _build_gathering_query(self, request: TripRequest) -> str:
        prefs = ", ".join(request.preferences) or "热门景点"
        return (
            f"我准备从 {request.start_date} 到 {request.end_date} "
            f"去 {request.city} 旅游 {request.travel_days} 天，"
            f"住宿偏好「{request.accommodation}」，"
            f"风格偏好「{prefs}」。\n"
            f"请用高德地图工具：\n"
            f"  1) 搜索 {request.city} 跟「{prefs}」相关的景点（关键词分别试 1-2 个）\n"
            f"  2) 查询 {request.city} 的天气\n"
            f"  3) 搜索 {request.city} 的「{request.accommodation}」候选酒店\n"
            f"信息齐全后，整理成清晰的素材文本（保留景点名、地址、经纬度），"
            f"调 Finish 返回。"
            f"{('额外要求：' + request.free_text_input) if request.free_text_input else ''}"
        )

    def _fallback_plan(self, request: TripRequest) -> TripPlan:
        """LLM / MCP 不可用时的占位计划，保证前端不空白"""
        try:
            start = datetime.strptime(request.start_date, "%Y-%m-%d")
        except ValueError:
            start = datetime.now()
        days = []
        for i in range(request.travel_days):
            d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
            days.append(
                DayPlan(
                    date=d,
                    day_index=i,
                    description=f"第 {i + 1} 天行程（占位，请配置 MCP 后重试）",
                    transportation=request.transportation,
                    attractions=[
                        Attraction(
                            name=f"{request.city} 景点 {j + 1}",
                            description="占位景点",
                        )
                        for j in range(2)
                    ],
                    meals=[
                        Meal(type="breakfast", name="早餐", description="占位"),
                        Meal(type="lunch", name="午餐", description="占位"),
                        Meal(type="dinner", name="晚餐", description="占位"),
                    ],
                )
            )
        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            overall_suggestions=(
                "当前为占位计划。请确认 .env 中 LLM_* 与 AMAP_MAPS_API_KEY "
                "已正确配置，并确保本机有 uvx 命令可用（pip install uv）。"
            ),
        )


# ============ 单例工厂 ============

_service: Optional[TripPlannerService] = None


def get_service() -> TripPlannerService:
    global _service
    if _service is None:
        _service = TripPlannerService()
    return _service
