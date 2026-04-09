# 模型微调实验平台

## 项目简介

构建一个完整的 LLM 微调实验平台，支持数据集准备、LoRA/QLoRA 微调、训练监控和模型评估，让微调流程标准化、可复现。

## 功能特性

- ✅ 数据集格式化和验证
- ✅ 多种数据格式支持（Alpaca、ShareGPT）
- ✅ LoRA/QLoRA 参数配置
- ✅ 训练过程监控
- ✅ 训练日志记录
- ✅ 模型合并导出
- ✅ 推理测试

## 项目结构

```
finetune-platform/
├── README.md              # 项目说明
├── requirements.txt       # 依赖列表
├── config.yaml           # 训练配置
├── prepare_data.py       # 数据准备脚本
├── train.py              # 训练脚本
├── merge_model.py        # 模型合并
├── inference.py          # 推理测试
├── data/                 # 数据目录
│   ├── raw/             # 原始数据
│   └── processed/       # 处理后数据
├── models/              # 模型目录
├── outputs/             # 输出目录
├── scripts/             # 工具脚本
│   ├── dataset_utils.py # 数据集工具
│   ├── training_utils.py # 训练工具
│   └── model_utils.py   # 模型工具
└── tests/               # 测试用例
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备数据集

```bash
# 将原始数据放入 data/raw/
# 运行数据处理脚本
python prepare_data.py --input data/raw/sample_data.json --format alpaca
```

### 3. 配置训练参数

编辑 `config.yaml`：

```yaml
model:
  name: Qwen/Qwen2.5-1.5B-Instruct

lora:
  r: 16
  alpha: 32
  dropout: 0.05

training:
  epochs: 3
  batch_size: 4
  learning_rate: 2e-4
```

### 4. 开始训练

```bash
python train.py --config config.yaml
```

### 5. 合并模型

```bash
python merge_model.py --adapter outputs/checkpoint-final --output models/merged
```

### 6. 测试推理

```bash
python inference.py --model models/merged
```

## 数据格式

### Alpaca 格式

```json
{
  "instruction": "将以下句子翻译成英文",
  "input": "今天天气很好",
  "output": "The weather is nice today"
}
```

### ShareGPT 格式

```json
{
  "conversations": [
    { "from": "human", "value": "你好" },
    { "from": "gpt", "value": "你好！有什么可以帮你的吗？" }
  ]
}
```

## 训练监控

```
Epoch 1/3:
  Step 100/500 | Loss: 2.345 | LR: 2e-4 | Time: 1:23:45
  Step 200/500 | Loss: 1.876 | LR: 1.8e-4 | Time: 2:47:30
  ...

评估结果:
  Perplexity: 8.56
  BLEU: 32.4
```

## 核心技术

### LoRA 原理

```
原始权重 W ──────────────────────────────→ 输出
         │                              ↑
         └──→ LoRA_A (r×d) → LoRA_B (d×r) ─┘
              (低秩分解)
```

### 关键参数

| 参数          | 说明     | 推荐值      |
| ------------- | -------- | ----------- |
| lora_r        | 秩       | 8-64        |
| lora_alpha    | 缩放因子 | 16-64       |
| lora_dropout  | Dropout  | 0.05-0.1    |
| learning_rate | 学习率   | 1e-4 - 5e-4 |
| batch_size    | 批次大小 | 4-16        |

## 技术栈

- Python 3.10+
- Transformers - 模型加载
- PEFT - LoRA 实现
- Datasets - 数据处理
- Accelerate - 分布式训练
- BitsAndBytes - 量化

## 注意事项

⚠️ **硬件要求**：

- LoRA: 建议 16GB+ 显存
- QLoRA: 可在 8GB 显存下运行

⚠️ **首次运行**会下载模型，请确保网络通畅

## License

MIT License
