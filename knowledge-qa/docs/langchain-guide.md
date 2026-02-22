# LangChain 入门指南

## 什么是 LangChain？

LangChain 是一个用于开发由语言模型驱动的应用程序的框架。它提供了一套工具和抽象，使得构建复杂的 LLM 应用变得更加简单。

## 核心组件

### 1. Models（模型）

Models 是 LangChain 的基础组件，提供与各种大语言模型的统一接口。

支持的模型类型：

- LLMs：纯文本补全模型
- Chat Models：对话模型，支持消息列表
- Text Embedding Models：文本向量化模型

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("你好")
```

### 2. Prompts（提示）

Prompts 用于管理和优化发送给语言模型的提示。

主要功能：

- 提示模板（PromptTemplate）
- 示例选择器（ExampleSelector）
- 输出解析器（OutputParser）

```python
from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    "你是一个{role}。请回答：{question}"
)
```

### 3. Chains（链）

Chains 将多个组件串联成一个工作流程。

常用的链类型：

- LLMChain：最基础的链
- SequentialChain：顺序执行多个链
- RouterChain：根据条件路由到不同的链

### 4. Memory（记忆）

Memory 用于在对话中保持状态和上下文。

记忆类型：

- ConversationBufferMemory：保存完整对话历史
- ConversationSummaryMemory：保存对话摘要
- ConversationBufferWindowMemory：保存最近 N 轮对话

### 5. Agents（代理）

Agents 使用 LLM 来决定采取哪些行动。

核心概念：

- Tools：代理可以使用的工具
- Agent Executor：执行代理决策的引擎
- ReAct：推理和行动的框架

## RAG（检索增强生成）

RAG 是 LangChain 的重要应用场景，通过检索外部知识来增强 LLM 的回答。

### RAG 流程

1. **文档加载**：从各种来源加载文档
2. **文档分割**：将长文档切分成小块
3. **向量化**：将文本转换为向量
4. **存储**：保存到向量数据库
5. **检索**：根据问题检索相关文档
6. **生成**：结合检索结果生成回答

### 向量数据库

常用的向量数据库：

- Chroma：轻量级，适合开发
- Pinecone：云服务，适合生产
- Milvus：开源，可自部署
- Qdrant：高性能，支持过滤

## 最佳实践

1. **合理设置 chunk_size**：根据文档类型调整
2. **使用重叠**：避免上下文断裂
3. **优化检索**：结合关键词和语义检索
4. **评估质量**：使用 RAGAs 等框架评估

## 总结

LangChain 提供了构建 LLM 应用的完整工具链，从简单的提示调用到复杂的 RAG 系统都能轻松实现。
