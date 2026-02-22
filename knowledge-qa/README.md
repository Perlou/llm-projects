# 个人知识库问答系统

## 项目简介

构建一个基于 RAG（检索增强生成）的个人文档知识库问答系统，支持导入各种格式的文档，通过自然语言进行智能问答。

## 功能特性

- ✅ 支持 PDF、Markdown、TXT 文档格式
- ✅ 智能文档分块（多种分割策略）
- ✅ 向量化存储和相似度检索
- ✅ 多轮对话（记住上下文）
- ✅ 答案来源引用
- ✅ 命令行交互界面

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入 OPENAI_API_KEY
```

### 3. 添加文档

将你的文档放入 `docs/` 目录，支持：

- `.pdf` - PDF 文档
- `.md` - Markdown 文件
- `.txt` - 纯文本文件

### 4. 运行程序

```bash
python main.py
```

## 使用示例

```
📚 个人知识库问答系统 v1.0

加载文档中...
✅ 已加载 5 个文档，共 234 个文本片段

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

命令:
  /add <path>  - 添加文档
  /list        - 查看已加载文档
  /clear       - 清除对话历史
  /quit        - 退出程序

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

问: LangChain 的核心组件有哪些？

答: 根据文档，LangChain 的核心组件包括：

1. **Models** - 提供与各种 LLM 的统一接口
2. **Prompts** - 用于管理和优化提示模板
3. **Chains** - 将多个组件串联成工作流
4. **Memory** - 管理对话状态和历史
5. **Agents** - 使用 LLM 决定执行哪些操作

📖 来源:
  • langchain-guide.md (第 15-42 行)
  • llm-basics.pdf (第 3 页)

问: 它们之间是如何协作的？

答: 基于上文提到的核心组件，它们的协作方式如下...
```

## 核心技术

### 文档处理流程

```
文档 → 加载 → 分块 → Embedding → 向量存储
                                    ↓
用户提问 → Embedding → 相似度检索 → 上下文
                                    ↓
                         提示词组装 → LLM → 回答
```

### 关键参数

| 参数          | 默认值      | 说明         |
| ------------- | ----------- | ------------ |
| chunk_size    | 500         | 文本块大小   |
| chunk_overlap | 100         | 块间重叠     |
| top_k         | 5           | 检索返回数量 |
| model         | gpt-4o-mini | 使用的 LLM   |

## 扩展建议

1. **支持更多格式**：添加 Word、Excel、HTML 支持
2. **混合检索**：结合 BM25 和向量检索
3. **Web 界面**：使用 Gradio 或 Streamlit
4. **持久化存储**：使用 Qdrant 或 Pinecone

## 技术栈

- Python 3.10+
- LangChain - LLM 应用框架
- OpenAI API - LLM 和 Embedding
- ChromaDB - 向量数据库
- Rich - 终端美化

## License

MIT License
