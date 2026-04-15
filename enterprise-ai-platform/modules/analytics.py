"""
数据分析模块
============

自然语言数据分析和可视化描述。
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import sys

sys.path.insert(0, str(__file__).rsplit("/", 1)[0].rsplit("/", 1)[0])
from services.llm_provider import get_llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


@dataclass
class AnalysisResult:
    """分析结果"""

    query: str
    interpretation: str
    result: Any
    code: Optional[str] = None
    chart_suggestion: Optional[str] = None


class DataAnalyzer:
    """数据分析器"""

    def __init__(self):
        pass

    def analyze_data(
        self,
        data: Dict[str, Any],
        question: str,
    ) -> AnalysisResult:
        """分析数据并回答问题"""
        llm = get_llm(temperature=0.2)

        prompt = ChatPromptTemplate.from_template("""你是一个数据分析专家。基于以下数据回答用户问题。

数据：
```json
{data}
```

问题：{question}

请：
1. 分析数据
2. 回答问题
3. 提供洞察

回答：""")

        chain = prompt | llm | StrOutputParser()
        result = chain.invoke(
            {
                "data": json.dumps(data, ensure_ascii=False, indent=2),
                "question": question,
            }
        )

        return AnalysisResult(
            query=question,
            interpretation=result,
            result=data,
        )

    def generate_pandas_code(
        self,
        question: str,
        columns: List[str],
        sample_data: List[Dict] = None,
    ) -> str:
        """生成 Pandas 分析代码"""
        llm = get_llm(temperature=0.1)

        prompt = ChatPromptTemplate.from_template("""你是一个 Python 数据分析专家。

数据框的列名：{columns}
示例数据：{sample}

用户需求：{question}

请生成 Pandas 代码来完成分析。假设数据框变量名为 `df`。
只输出代码，不要其他解释。

```python
""")

        chain = prompt | llm | StrOutputParser()
        result = chain.invoke(
            {
                "columns": ", ".join(columns),
                "sample": json.dumps(
                    sample_data[:3] if sample_data else [], ensure_ascii=False
                ),
                "question": question,
            }
        )

        # 清理代码
        code = result.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]

        return code.strip()

    def generate_sql(
        self,
        question: str,
        table_schema: str,
    ) -> str:
        """生成 SQL 查询"""
        llm = get_llm(temperature=0.1)

        prompt = ChatPromptTemplate.from_template("""你是一个 SQL 专家。

表结构：
{schema}

用户需求：{question}

请生成 SQL 查询语句。只输出 SQL，不要其他解释。

```sql
""")

        chain = prompt | llm | StrOutputParser()
        result = chain.invoke(
            {
                "schema": table_schema,
                "question": question,
            }
        )

        # 清理 SQL
        sql = result.strip()
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]

        return sql.strip()

    def describe_trend(self, data_description: str) -> str:
        """描述数据趋势"""
        llm = get_llm(temperature=0.3)

        prompt = ChatPromptTemplate.from_template("""分析以下数据的趋势和特点：

{description}

请提供：
1. 整体趋势描述
2. 关键转折点
3. 可能的原因分析
4. 预测建议

分析：""")

        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"description": data_description})

    def suggest_visualization(self, data_description: str) -> str:
        """建议可视化方案"""
        llm = get_llm(temperature=0.3)

        prompt = ChatPromptTemplate.from_template("""基于以下数据描述，建议最合适的可视化方案：

数据描述：{description}

请建议：
1. 最佳图表类型
2. 图表配置建议
3. 关键展示要素
4. 交互功能建议

建议：""")

        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"description": data_description})


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        pass

    def generate_report(
        self,
        title: str,
        data_summary: str,
        analyses: List[str],
        format: str = "markdown",
    ) -> str:
        """生成分析报告"""
        llm = get_llm(temperature=0.4)

        prompt = ChatPromptTemplate.from_template("""生成一份专业的数据分析报告。

标题：{title}

数据概述：
{summary}

分析结果：
{analyses}

请生成格式为 {format} 的完整报告，包括：
1. 摘要
2. 数据概述
3. 分析发现
4. 结论和建议

报告：""")

        chain = prompt | llm | StrOutputParser()
        return chain.invoke(
            {
                "title": title,
                "summary": data_summary,
                "analyses": "\n\n".join(analyses),
                "format": format,
            }
        )


# 便捷函数
def natural_language_query(data: Dict, question: str) -> str:
    """自然语言查询数据"""
    analyzer = DataAnalyzer()
    result = analyzer.analyze_data(data, question)
    return result.interpretation
