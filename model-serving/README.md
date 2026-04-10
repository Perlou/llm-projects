# 模型部署服务

> 掌握 LLM 生产部署技术

## 项目简介

构建生产级别的 LLM 推理服务，支持多种后端（vLLM/TGI/Transformers）、流式输出、负载均衡，并提供 Docker 容器化部署方案。

## 功能特性

- ✅ FastAPI RESTful API
- ✅ OpenAI 兼容接口
- ✅ 流式输出 (SSE)
- ✅ 多推理后端支持
- ✅ 请求队列管理
- ✅ 健康检查和监控
- ✅ Docker 容器化

## 项目结构

```
model-serving/
├── README.md              # 项目说明
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
├── Dockerfile            # Docker 构建文件
├── docker-compose.yaml   # Docker Compose 配置
├── main.py               # 服务入口
├── app/                  # 应用模块
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   ├── models.py         # 数据模型
│   ├── api.py            # API 路由
│   ├── engine.py         # 推理引擎
│   └── middleware.py     # 中间件
├── scripts/              # 工具脚本
│   ├── healthcheck.py    # 健康检查
│   └── benchmark.py      # 性能测试
└── tests/                # 测试用例
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 设置模型路径等
```

### 3. 启动服务

```bash
# 开发模式
python main.py

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Docker 部署

```bash
# 构建镜像
docker build -t llm-serving .

# 启动容器
docker-compose up -d
```

## API 文档

启动服务后访问：http://localhost:8000/docs

### 核心接口

#### 聊天补全 (OpenAI 兼容)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "default",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": false
  }'
```

#### 流式输出

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "default",
    "messages": [{"role": "user", "content": "写一首诗"}],
    "stream": true
  }'
```

#### 健康检查

```bash
curl http://localhost:8000/health
```

## 推理后端

| 后端             | 特点     | 推荐场景 |
| ---------------- | -------- | -------- |
| **transformers** | 简单易用 | 开发测试 |
| **vLLM**         | 高吞吐量 | 生产环境 |
| **TGI**          | 功能丰富 | 企业部署 |

## 性能优化

### 关键配置

```env
# 推理引擎
INFERENCE_ENGINE=transformers  # vllm / tgi

# 批处理
MAX_BATCH_SIZE=8
MAX_CONCURRENT_REQUESTS=100

# 模型优化
USE_FLASH_ATTENTION=true
LOAD_IN_8BIT=false
```

### 性能测试

```bash
python scripts/benchmark.py --url http://localhost:8000 --requests 100
```

## 监控指标

服务提供以下监控端点：

- `/health` - 健康状态
- `/metrics` - Prometheus 指标
- `/stats` - 服务统计

## 技术栈

- Python 3.10+
- FastAPI - Web 框架
- Uvicorn - ASGI 服务器
- Transformers - 模型推理
- Docker - 容器化

## License

MIT License
