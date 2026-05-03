# CLAUDE.md

本文件为 Claude（及其他 AI 助手）在操作此仓库时提供必要的上下文和指引。

## 项目概述

这是一个个人 LLM/AI 应用开发积累仓库。每个子目录都是**独立的项目**，拥有自己的虚拟环境、依赖和配置文件，不存在共享运行时或 monorepo 构建体系。

## 仓库结构

```
llm-projects/
├── .env.example            # 根目录 API Key 模板（各项目共同参考）
├── .env                    # 实际 Key 文件（已 gitignore）
├── chatbot/                # 流式输出聊天机器人（Gradio 界面）
├── writing-assistant/      # 基于 Gemini 的写作助手
├── data-extractor/         # LangChain + Pydantic 结构化信息提取
├── knowledge-qa/           # RAG 知识库问答系统
├── enterprise-search/      # 混合检索搜索引擎（BM25 + 向量 + Rerank）
├── multi-model-chat/       # 多 LLM 并排对比聊天
├── multimodal-analysis/    # Gemini 2.0 多模态内容分析平台
├── research-assistant/     # ReAct Agent 自动化文献研究助手
├── enterprise-ai-platform/ # 功能完整的企业级 AI 平台
├── security-guard/         # LLM 安全防护（注入检测、PII 过滤等）
├── finetune-platform/      # LoRA/QLoRA 微调实验平台
├── model-serving/          # 生产级 LLM 推理服务（支持 Docker）
└── trip-planner/           # 基于高德地图 MCP 的旅行规划 Agent
```

## 操作各子项目的通用约定

### 基本约定

- **每个项目完全独立**，操作前务必先 `cd` 进入对应项目目录。
- **虚拟环境**位于 `<项目目录>/venv/`，激活命令：`source venv/bin/activate`。
- **入口文件**：命令行模式通常为 `main.py`，FastAPI 服务通常为 `app.py`，个别项目有所不同。
- **环境变量**从各项目目录下的 `.env` 文件读取；部分项目也会读取根目录的 `.env`。

### 典型启动流程

```bash
cd <项目名>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 若该项目有独立的 .env.example
python main.py
```

### 启动 API 服务

含 FastAPI 服务的项目（`enterprise-ai-platform`、`multimodal-analysis`、`model-serving`、`trip-planner/backend`）：

```bash
uvicorn app:app --reload           # 或 app.api.main:app
# API 文档：http://localhost:8000/docs
```

## 各项目特殊说明

### trip-planner
- 含独立前端，目录名为 `frontent/`（注意：原目录名有拼写错误），基于 Vue 3 + TypeScript + Vite 构建。
- 后端使用 **HelloAgents** 框架，集成高德地图 MCP Server。
- 需要配置高德地图 API Key（Web 服务 API + JS API 两种类型）以及 LLM API Key。
- 启动后端：`uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000`
- 启动前端：`cd frontent && npm install && npm run dev`

### finetune-platform
- 对显存要求较高：LoRA 建议 16GB+ 显存，QLoRA 可在 8GB 显存下运行。
- 训练配置在 `config.yaml` 中，而非 `.env`。
- 标准工作流：`prepare_data.py` → `train.py` → `merge_model.py` → `inference.py`

### model-serving
- 支持三种推理后端：`transformers`（开发测试）、`vLLM`（生产环境）、`TGI`（企业部署）。
- 含 `Dockerfile` 和 `docker-compose.yaml`，支持容器化部署。
- 对外提供 OpenAI 兼容接口 `/v1/chat/completions`。
- Docker 部署主要针对 Linux；macOS 上 GPU 直通需要额外配置。

### enterprise-ai-platform
- LLM 提供商可通过 `.env` 切换：Gemini（默认）或 Ollama（本地）。
- 同时支持 CLI 模式（`python main.py`）和 API 服务模式（`python app.py`）。
- 使用 ChromaDB 存储向量，知识库数据存放在 `data/knowledge_bases/`。

### multimodal-analysis
- 需要 Gemini API Key（`GOOGLE_API_KEY`）。
- 图像、图表、视频、音频分析分别由 `analyzers/` 目录下的独立模块处理。
- 视频处理依赖 `moviepy`；音频需确保格式兼容。

### security-guard
- 核心规则引擎**无需 LLM API Key** 即可运行。
- OpenAI API 为可选配置，仅用于 AI 辅助内容审核功能。

## 各项目 API Key 对照

| 提供商 | 环境变量 | 使用该 Key 的项目 |
|--------|---------|-----------------|
| OpenAI | `OPENAI_API_KEY` | chatbot, knowledge-qa, enterprise-search, multi-model-chat, research-assistant, security-guard |
| Anthropic | `ANTHROPIC_API_KEY` | multi-model-chat |
| Google Gemini | `GOOGLE_API_KEY` | writing-assistant, data-extractor, multimodal-analysis, enterprise-ai-platform |
| Ollama（本地） | `OLLAMA_HOST` | enterprise-ai-platform, multi-model-chat |
| 高德地图 | `AMAP_MAPS_API_KEY` | trip-planner |

## 代码模式说明

### sys.path 操作
部分项目在脚本顶部动态修改 `sys.path`，以确保无论从哪个目录执行脚本，项目级模块都能被正确导入。这是**有意为之**，请勿删除。

### LangChain 版本
代码库使用 **LangChain 0.3+**，迁移注意事项：
- 使用 `langchain_core.documents` 而非 `langchain.schema`
- 第三方集成使用 `langchain_community`
- 推荐使用 LCEL（`|` 运算符）构建 Chain

### 异步处理
`multi-model-chat` 使用 `asyncio` 实现多模型并发调用，修改时注意 `async/await` 的正确性及事件循环的管理。

### Pydantic 模型
`data-extractor` 使用 Pydantic v2，字段定义采用 `model_config` 模式，请勿使用已废弃的 `class Config` 写法。

## 测试

各项目均含 `tests/` 目录，在对应项目下运行：

```bash
cd <项目名>
source venv/bin/activate
python -m pytest tests/ -v
```

不存在根目录级别的统一测试运行器，测试必须逐项目运行。

## 注意事项

- **不要**全局安装依赖包，始终使用项目自己的 `venv`。
- **不要**跨项目共享虚拟环境。
- **不要**提交 `.env` 文件，已在 `.gitignore` 中排除。
- 运行 `finetune-platform/train.py` 前，**务必**先确认 GPU 可用性。
- `model-serving` 的 Docker 部署主要面向 Linux 环境，macOS 上 GPU 直通需要额外配置。
