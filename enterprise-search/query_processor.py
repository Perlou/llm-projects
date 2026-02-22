"""
查询处理模块
查询扩展和改写
"""

from typing import List
import google.generativeai as genai

from config import config


class QueryProcessor:
    """查询处理器"""

    EXPANSION_PROMPT = """你是一个搜索查询扩展助手。给定用户的搜索查询，生成 3-5 个相关的扩展查询词，帮助提高搜索的召回率。

原始查询: {query}

要求：
1. 生成同义词、近义词
2. 生成相关概念
3. 考虑中英文表达
4. 用逗号分隔

扩展查询词:"""

    REWRITE_PROMPT = """你是一个搜索查询改写助手。将用户的口语化查询改写为更适合检索的形式。

原始查询: {query}

要求：
1. 提取核心关键词
2. 去除无意义的词
3. 保持原意不变

改写后的查询:"""

    def __init__(self):
        genai.configure(api_key=config.google_api_key)
        self.model = genai.GenerativeModel(config.llm_model)

    def expand_query(self, query: str) -> List[str]:
        """查询扩展"""
        try:
            response = self.model.generate_content(
                self.EXPANSION_PROMPT.format(query=query),
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=100,
                ),
            )

            expanded = response.text.strip()
            # 解析扩展词
            terms = [t.strip() for t in expanded.split(",") if t.strip()]
            return terms

        except Exception as e:
            print(f"查询扩展失败: {e}")
            return []

    def rewrite_query(self, query: str) -> str:
        """查询改写"""
        try:
            response = self.model.generate_content(
                self.REWRITE_PROMPT.format(query=query),
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=50,
                ),
            )

            return response.text.strip()

        except Exception as e:
            print(f"查询改写失败: {e}")
            return query

    def process(self, query: str, expand: bool = True, rewrite: bool = False) -> dict:
        """处理查询"""
        result = {
            "original": query,
            "processed": query,
            "expanded_terms": [],
        }

        if rewrite:
            result["processed"] = self.rewrite_query(query)

        if expand:
            result["expanded_terms"] = self.expand_query(query)

        return result
