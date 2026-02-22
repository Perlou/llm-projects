# 结构化数据提取器 (Data Extractor)

## 项目简介

基于 LangChain 的结构化数据提取工具，从非结构化文本中提取结构化信息。
这是（LangChain 基础）的实战项目，综合运用了课程中学到的：

- LCEL 表达式
- Pydantic 输出解析器
- 链式调用
- 多步骤处理

## 功能特性

- 📋 **简历提取**：从简历文本提取个人信息、教育经历、工作经验
- 📄 **合同分析**：提取合同关键条款和信息
- 📰 **新闻抽取**：提取新闻事件的人物、时间、地点
- 💬 **情感分析**：分析产品评论的情感倾向
- 📊 **多格式导出**：支持 JSON/CSV 导出

## 技术栈

- Python 3.10+
- LangChain + LangChain-OpenAI
- Pydantic (数据模型)
- Google Generative AI (Gemini)
- Rich (终端美化)

## 快速开始

### 1. 安装依赖

```bash
cd data-extractor
pip install -r requirements.txt
```

### 2. 配置环境

确保项目根目录的 `.env` 文件包含：

```
GOOGLE_API_KEY=your-gemini-api-key
```

### 3. 运行

```bash
# 交互式模式
python main.py

# 命令行模式
python main.py --mode resume --input "张三，男，1990年出生..."
```

## 使用示例

```
📊 结构化数据提取器
━━━━━━━━━━━━━━━━━━━━

选择提取模式:
  [1] 📋 简历信息提取
  [2] 📄 合同条款提取
  [3] 📰 新闻事件抽取
  [4] 💬 评论情感分析
  [q] 退出

请选择 [1-4]: 1

请输入文本（输入空行结束）:
张三，男，1990年5月出生于北京
2012年毕业于北京大学计算机科学专业
2012-2018 在百度担任软件工程师
2018-至今 在字节跳动担任技术总监

[提取中...]

📋 提取结果:
{
  "name": "张三",
  "gender": "男",
  "birth_date": "1990-05",
  "birthplace": "北京",
  "education": [
    {
      "school": "北京大学",
      "major": "计算机科学",
      "graduation_year": 2012
    }
  ],
  "work_experience": [
    {
      "company": "百度",
      "position": "软件工程师",
      "start_year": 2012,
      "end_year": 2018
    },
    {
      "company": "字节跳动",
      "position": "技术总监",
      "start_year": 2018,
      "end_year": null
    }
  ]
}

💾 已保存到 output/resume_20240127_133500.json
```

## 项目结构

```
data-extractor/
├── README.md
├── requirements.txt
├── main.py              # 主入口
├── config.py            # 配置
├── schemas/             # Pydantic 数据模型
│   ├── resume.py
│   ├── contract.py
│   ├── news.py
│   └── review.py
├── extractors/          # 提取器实现
│   ├── base.py
│   └── langchain_extractor.py
└── utils/
    └── display.py
```

## 学习要点

1. **Pydantic 数据模型**：定义结构化输出格式
2. **LangChain 输出解析器**：PydanticOutputParser
3. **LCEL 链式调用**：prompt | llm | parser
4. **错误处理**：解析失败的重试逻辑

## 扩展练习

1. 添加更多提取场景（发票、名片等）
2. 支持批量处理文件
3. 添加提取结果的可视化展示
4. 集成 OCR 支持图片提取
