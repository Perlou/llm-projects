# 多模型对比聊天应用 (Multi-Model Chat)

## 项目简介

这是一个支持多个 LLM 的聊天应用，可以对比不同模型对同一问题的回答。

- 多模型 API 调用（OpenAI、Claude、Gemini、Ollama）
- 流式响应处理
- 错误处理与重试
- 速率限制

## 功能特性

- 🔄 **多模型支持**：同时调用多个 LLM
- 📊 **对比展示**：并排展示不同模型的回答
- ⚡ **流式输出**：实时显示回答
- 📈 **性能统计**：首字延迟、总耗时、Token 消耗
- 💰 **成本估算**：预估 API 调用成本
- 🔒 **错误处理**：优雅处理 API 错误

## 技术栈

- Python 3.10+
- OpenAI SDK
- Anthropic SDK
- Google GenerativeAI
- Rich (终端美化)
- asyncio (异步处理)

## 快速开始

### 1. 环境准备

```bash
cd projects/multi-model-chat
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env 填入 API Key
```

### 3. 运行应用

```bash
# 命令行交互模式
python main.py

# 单次对比查询
python main.py --query "什么是机器学习？"

# 指定模型
python main.py --models gemini-pro gpt-4 claude-3-sonnet --query "你好"
```

## 项目结构

```
multi-model-chat/
├── README.md           # 项目说明
├── requirements.txt    # 依赖
├── .env.example        # 环境变量模板
├── main.py             # 主入口
├── config.py           # 配置
├── models/
│   ├── __init__.py
│   ├── base.py         # 基类
│   ├── openai_model.py # OpenAI 模型
│   ├── claude_model.py # Claude 模型
│   ├── gemini_model.py # Gemini 模型
│   └── ollama_model.py # Ollama 模型
├── ui/
│   ├── __init__.py
│   └── terminal.py     # 终端界面
└── utils/
    ├── __init__.py
    └── stats.py        # 统计工具
```

## 使用示例

```
$ python main.py

🤖 多模型对比聊天应用
输入问题，按 Enter 发送，输入 'quit' 退出

👤 你: 用一句话解释什么是人工智能

┌─────────────────────────────────────────────────────────────┐
│ GPT-4 (1.2s)                                                │
├─────────────────────────────────────────────────────────────┤
│ 人工智能是让计算机模拟人类智能行为的技术。                  │
│ 📊 Tokens: 45 | 💰 $0.0013                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Claude 3.5 Sonnet (0.9s)                                    │
├─────────────────────────────────────────────────────────────┤
│ 人工智能是使计算机能够执行通常需要人类智慧的任务的技术。    │
│ 📊 Tokens: 52 | 💰 $0.0016                                   │
└─────────────────────────────────────────────────────────────┘
```

## 学习要点

通过这个项目，你将学会：

1. **统一 API 接口设计**：如何封装不同 LLM 的 API
2. **异步并发处理**：同时调用多个模型
3. **流式响应处理**：实时显示输出
4. **错误处理**：处理不同类型的 API 错误
5. **性能测量**：测量 TTFT 和总响应时间

## 扩展练习

1. 添加对话历史支持
2. 实现结果导出（Markdown/JSON）
3. 添加更多模型支持
4. 实现 Web 界面版本

## 参考资料

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Anthropic API 文档](https://docs.anthropic.com)
- [Rich 库文档](https://rich.readthedocs.io)
