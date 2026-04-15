# 企业级 AI 平台

> 综合运用所有 LLM 技术构建的企业级 AI 平台

## 项目简介

构建一个功能完整的企业级 AI 平台。

### 核心功能

| 功能        | 描述                             |
| ----------- | -------------------------------- |
| 💬 智能对话 | 多轮对话，流式响应，会话管理     |
| 📚 知识库   | 多知识库管理，文档导入，RAG 问答 |
| 📄 文档处理 | 摘要生成，信息提取，文档对比     |
| ✏️ 内容创作 | 多风格文章生成，内容优化         |
| 🤖 Agent    | 工作流自动化，工具调用           |
| 🌐 API 服务 | RESTful API，支持第三方集成      |

### 技术栈

- **LLM**: Gemini 2.0 Flash / Ollama + Qwen
- **向量数据库**: ChromaDB
- **API 框架**: FastAPI
- **CLI**: Rich + Typer

## 快速开始

### 1. 环境准备

```bash
cd enterprise-ai-platform

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入 GOOGLE_API_KEY
```

**获取 API Key**: https://aistudio.google.com/apikey

### 3. 运行应用

#### 命令行模式

```bash
python main.py
```

#### API 服务模式

```bash
python app.py
# 或
uvicorn app:app --reload
```

API 文档: http://localhost:8000/docs

## 项目结构

```
enterprise-ai-platform/
├── main.py              # CLI 入口
├── app.py               # FastAPI 应用
├── config.py            # 配置管理
├── services/            # 核心服务
│   ├── llm_provider.py  # LLM 提供者
│   ├── knowledge_base.py # 知识库服务
│   ├── chat.py          # 对话服务
│   └── agent.py         # Agent 服务
├── modules/             # 功能模块
│   ├── qa.py            # 智能问答
│   ├── document.py      # 文档处理
│   ├── analytics.py     # 数据分析
│   └── content.py       # 内容创作
├── routes/              # API 路由
│   ├── chat.py          # 对话 API
│   ├── knowledge.py     # 知识库 API
│   └── document.py      # 文档 API
└── data/                # 数据目录
    ├── knowledge_bases/ # 知识库存储
    └── uploads/         # 上传文件
```

## 使用指南

### CLI 模式

运行 `python main.py` 后，选择功能菜单：

```
┌─────────────────────────────────┐
│  🏢 企业级 AI 平台              │
│  综合性 AI 服务平台             │
└─────────────────────────────────┘

功能菜单
┌────┬─────────────────┐
│ 1  │ 💬 智能对话     │
│ 2  │ 📚 知识库管理   │
│ 3  │ 🔍 知识问答     │
│ 4  │ 📄 文档处理     │
│ 5  │ ✏️  内容创作     │
│ 6  │ 🤖 Agent 任务   │
│ 7  │ 🌐 启动 API     │
└────┴─────────────────┘
```

### API 模式

主要端点：

| 端点                            | 方法     | 描述       |
| ------------------------------- | -------- | ---------- |
| `/api/chat`                     | POST     | 对话       |
| `/api/chat/stream`              | POST     | 流式对话   |
| `/api/knowledge`                | GET/POST | 知识库管理 |
| `/api/knowledge/{id}/documents` | POST     | 上传文档   |
| `/api/knowledge/{id}/query`     | POST     | 知识库问答 |
| `/api/document/summarize`       | POST     | 文档摘要   |

## 模型配置

### 使用 Gemini (默认)

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.0-flash
```

### 使用 Ollama 本地模型

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
```

确保 Ollama 服务已启动：`ollama serve`

## 学习要点

1. **多模型适配**: 统一接口支持多种 LLM
2. **模块化设计**: 服务层和功能层分离
3. **RAG 系统**: 多知识库管理和检索
4. **Agent 工作流**: ReAct 推理和工具调用
5. **API 设计**: RESTful 风格，流式响应
6. **配置管理**: 环境变量和默认值

## 扩展建议

- 添加用户认证和权限管理
- 实现对话历史持久化
- 添加更多 Agent 工具
- 集成更多 LLM 提供商
- 添加前端界面

