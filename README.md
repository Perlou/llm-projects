# 🤖 LLM Projects

> 个人 AI / LLM 相关应用的开发积累，涵盖 RAG、Agent、多模态、微调、模型部署等核心方向。

---

## 📁 项目一览

| 项目 | 简介 | 技术栈 |
|------|------|--------|
| [chatbot](./chatbot) | 流式输出 + 多轮对话的智能聊天机器人，提供 Gradio Web 界面 | OpenAI, Gradio |
| [writing-assistant](./writing-assistant) | 基于 Gemini 的写作助手，支持多种写作模式和风格定制 | Gemini, Rich |
| [data-extractor](./data-extractor) | 从非结构化文本中提取结构化信息（简历、合同、新闻等） | LangChain, Pydantic, Gemini |
| [knowledge-qa](./knowledge-qa) | 基于 RAG 的个人文档知识库问答系统 | LangChain, ChromaDB, OpenAI |
| [enterprise-search](./enterprise-search) | 企业级混合检索搜索引擎（BM25 + 向量 + Rerank） | LangChain, ChromaDB, sentence-transformers |
| [multi-model-chat](./multi-model-chat) | 同时调用多个 LLM 并排展示对比结果 | OpenAI, Anthropic, Gemini, asyncio |
| [multimodal-analysis](./multimodal-analysis) | 基于 Gemini 2.0 的多模态内容分析平台（图像/图表/视频/音频） | Gemini, LangChain, ChromaDB |
| [research-assistant](./research-assistant) | ReAct Agent 研究助手，自动搜索、阅读、整理文献并生成报告 | LangChain, OpenAI, DuckDuckGo |
| [enterprise-ai-platform](./enterprise-ai-platform) | 功能完整的企业级 AI 平台（对话/知识库/文档/Agent/API） | Gemini/Ollama, ChromaDB, FastAPI |
| [security-guard](./security-guard) | LLM 应用安全防护（注入检测、越狱防护、PII 过滤、内容审核） | OpenAI, Rich |
| [finetune-platform](./finetune-platform) | LLM 微调实验平台，支持 LoRA/QLoRA 微调全流程 | Transformers, PEFT, Accelerate |
| [model-serving](./model-serving) | 生产级 LLM 推理服务，OpenAI 兼容接口，支持 Docker 部署 | FastAPI, vLLM/TGI/Transformers, Docker |

---

## 🛠️ 技术栈概览

- **LLM**：OpenAI GPT-4, Anthropic Claude, Google Gemini, Ollama (本地)
- **Agent 框架**：LangChain, HelloAgents
- **向量数据库**：ChromaDB, Pinecone
- **后端**：FastAPI, Python 3.10+
- **前端**：Vue 3 + TypeScript + Vite（trip-planner）
- **微调**：Transformers, PEFT (LoRA/QLoRA), Accelerate, BitsAndBytes
- **部署**：Docker, Uvicorn, vLLM, TGI

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone <repo-url>
cd llm-projects
```

### 2. 配置全局 API Keys

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Keys
```

`.env.example` 支持以下 Key 配置：

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
HUGGINGFACE_TOKEN=hf_...
COHERE_API_KEY=...
OLLAMA_HOST=http://localhost:11434
```

### 3. 进入具体项目

```bash
cd ./chatbot           # 以 chatbot 为例

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

> 每个子项目有独立的 `README.md`，详细说明了功能介绍、配置方式和运行步骤。

---

## 📌 项目分类

### 🔍 检索与知识库
- **knowledge-qa** — RAG 知识库问答
- **enterprise-search** — 混合检索搜索引擎

### 🤖 Agent 与自动化
- **research-assistant** — ReAct Agent 文献研究
- **trip-planner** — MCP 工具调用旅行规划
- **enterprise-ai-platform** — 综合 Agent 工作流

### 💬 对话与生成
- **chatbot** — 多轮对话机器人
- **multi-model-chat** — 多模型对比
- **writing-assistant** — 写作助手

### 🖼️ 多模态
- **multimodal-analysis** — 图像/图表/视频/音频分析
- **data-extractor** — 结构化信息提取

### ⚙️ 基础设施
- **finetune-platform** — LoRA/QLoRA 微调
- **model-serving** — 生产部署服务
- **security-guard** — 安全防护

---

## 📄 License

MIT License
