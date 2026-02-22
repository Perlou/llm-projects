"""
LangChain 提取器
使用 LCEL 和 PydanticOutputParser 实现结构化数据提取
"""

from typing import Type, TypeVar
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from config import GOOGLE_API_KEY, GEMINI_MODEL
from schemas import ResumeInfo, ContractInfo, NewsEvent, ReviewAnalysis

T = TypeVar("T", bound=BaseModel)


# 各类型的提取提示词
EXTRACTION_PROMPTS = {
    "resume": """你是一个专业的简历信息提取专家。请从以下文本中提取结构化的简历信息。

注意事项：
- 仔细识别姓名、性别、出生日期等个人信息
- 准确提取教育经历，包括学校、专业、学位、毕业年份
- 完整提取工作经历，包括公司、职位、起止时间
- 如果某些信息不存在，请使用 null

{format_instructions}

文本内容：
{text}
""",
    "contract": """你是一个专业的合同分析专家。请从以下合同文本中提取关键信息。

注意事项：
- 识别合同类型和标题
- 提取所有合同方信息
- 注意合同的有效期限和金额
- 提取关键条款和违约责任

{format_instructions}

合同文本：
{text}
""",
    "news": """你是一个专业的新闻分析专家。请从以下新闻文本中提取事件信息。

注意事项：
- 准确识别事件类型
- 提取涉及的人物、组织、地点
- 确定事件发生时间
- 概括事件的影响

{format_instructions}

新闻文本：
{text}
""",
    "review": """你是一个专业的评论分析专家。请分析以下产品评论的情感倾向。

注意事项：
- 判断整体情感是正面、负面还是中性
- 分析各个方面（价格、质量、服务等）的情感
- 提炼评论的关键点
- 判断用户是否推荐

{format_instructions}

评论文本：
{text}
""",
}

# 模式到 Schema 的映射
SCHEMA_MAP = {
    "resume": ResumeInfo,
    "contract": ContractInfo,
    "news": NewsEvent,
    "review": ReviewAnalysis,
}


class LangChainExtractor:
    """基于 LangChain 的结构化数据提取器"""

    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY 未配置")

        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0,  # 提取任务使用低温度
        )

    def extract(self, text: str, mode: str) -> BaseModel:
        """提取结构化数据

        Args:
            text: 待提取的文本
            mode: 提取模式 (resume/contract/news/review)

        Returns:
            对应的 Pydantic 模型实例
        """
        schema_class = SCHEMA_MAP.get(mode)
        if not schema_class:
            raise ValueError(f"不支持的模式: {mode}")

        prompt_template = EXTRACTION_PROMPTS.get(mode)
        if not prompt_template:
            raise ValueError(f"未找到对应的提示词: {mode}")

        # 创建输出解析器
        parser = PydanticOutputParser(pydantic_object=schema_class)

        # 创建提示词模板
        prompt = ChatPromptTemplate.from_template(prompt_template)

        # 构建 LCEL 链
        chain = prompt | self.llm | parser

        # 执行提取
        result = chain.invoke(
            {
                "text": text,
                "format_instructions": parser.get_format_instructions(),
            }
        )

        return result

    def extract_to_dict(self, text: str, mode: str) -> dict:
        """提取并返回字典格式"""
        result = self.extract(text, mode)
        return result.model_dump()
