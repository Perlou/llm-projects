# ClearAgent 旅行规划助手 🌍✈️

基于 [**clear-agent**](https://github.com/Perlou/clear-agent) 框架构建的全栈旅行规划 demo —— 集成高德地图 MCP 服务，由 LLM 自动生成多日行程。

## ✨ 它如何展示 ClearAgent 的能力

| ClearAgent 能力 | 在本 demo 里的体现 |
|---|---|
| **MCP 客户端** | `MCPClient.connect_stdio("uvx", ["amap-mcp-server"])` 一行接入高德 |
| **工具自动注册** | `client.register_to(registry)` 把 `maps_text_search` / `maps_weather` 等 MCP 工具一次性灌进 ToolRegistry |
| **ReActAgent + 原生 Function Calling** | `ReActAgent` 自动多轮调 MCP 工具收集景点 / 天气 / 酒店，无需正则解析 `[TOOL_CALL:...]` |
| **结构化输出** | `llm.with_structured_output(TripPlan)` 直出 Pydantic 实例，无需手工 `json.loads` |
| **统一 LLM 抽象** | 通过 `LLM_BASE_URL` 自动适配 OpenAI / DeepSeek / 阿里 / 任何兼容 OpenAI 协议的服务 |

## 🏗️ 项目结构

```
trip-planner/
├── README.md                      ← 本文件
├── backend/
│   ├── requirements.txt           ← 复制出去时使用
│   ├── .env.example
│   ├── run.py                     ← uvicorn 启动入口
│   └── app/
│       ├── config.py              ← pydantic-settings
│       ├── schemas.py             ← TripRequest / TripPlan
│       ├── agent.py               ← MCPClient + ReActAgent + StructuredLLM
│       └── main.py                ← FastAPI 路由
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.ts / App.vue / api.ts / types.ts
        └── views/
            ├── Home.vue           ← 输入表单
            └── Result.vue         ← 行程展示
```

## 🚀 快速开始

### 0. 前置条件

- Python ≥ 3.10
- Node.js ≥ 18
- 高德开放平台「Web 服务 API」Key —— 在 https://lbs.amap.com/ 申请
- 任一 OpenAI 兼容 LLM 的 Key（DeepSeek / Kimi / OpenAI / 阿里百炼 …）

### 1. 后端

```bash
cd backend

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 编辑 .env

python run.py
```

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

> 💡 首次请求会触发 `uvx amap-mcp-server` 启动 MCP 子进程；
> 如果你没装 `uv`，可以先 `pip install uv`，或自己改 `app/agent.py` 里的 `command="uvx"` 为本地 amap-mcp-server 命令。

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173 即可。

Vite 已经配好 `/api` → `http://localhost:8000` 的代理，无需改后端 CORS。

## 📝 使用流程

1. 在首页填写：目的地、日期、交通、住宿、风格偏好、额外要求
2. 点击「🚀 生成旅行计划」
3. 后端会：
   1. 用 `ReActAgent` 多轮自动调用高德 MCP（`maps_text_search` / `maps_weather`）收集真实素材
   2. 将素材连同需求喂给 `with_structured_output(TripPlan)`，直出结构化 Pydantic 对象
   3. 返回给前端
4. 前端展示：每日行程 / 景点 / 天气 / 餐饮 / 酒店 / 预算

## 🔧 核心代码片段（`backend/app/agent.py`）

```python
from clear_agent.agents.react_agent import ReActAgent
from clear_agent.core.llm import ClearAgentLLM
from clear_agent.mcp.client import MCPClient
from clear_agent.tools.registry import ToolRegistry

# 1) 把高德 MCP 工具一次性接入
registry = ToolRegistry()
client = MCPClient.connect_stdio(
    command="uvx", args=["amap-mcp-server"],
    env={"AMAP_MAPS_API_KEY": "your-key"},
)
client.register_to(registry)

# 2) ReAct Agent 自动多轮 Function Calling
agent = ReActAgent(
    name="旅行规划助手",
    llm=ClearAgentLLM(),
    tool_registry=registry,
    max_steps=10,
)
material = agent.run("帮我搜北京的历史文化景点 + 天气 + 经济型酒店")

# 3) 结构化输出 —— 直出 Pydantic
structured_llm = ClearAgentLLM().with_structured_output(TripPlan)
plan: TripPlan = structured_llm.invoke([
    {"role": "system", "content": "你是旅行规划专家"},
    {"role": "user", "content": f"基于素材规划行程：\n{material}"},
])
```


