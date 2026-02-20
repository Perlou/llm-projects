"""
Gemini 客户端
"""

import google.generativeai as genai
from typing import Generator
from config import GOOGLE_API_KEY, GEMINI_MODEL, GENERATION_CONFIG


class GeminiClient:
    """Gemini API 客户端"""

    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY 未配置，请检查 .env 文件")

        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL, generation_config=GENERATION_CONFIG
        )

    def generate(self, prompt: str) -> str:
        """生成内容（非流式）"""
        response = self.model.generate_content(prompt)
        return response.text

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """生成内容（流式）"""
        response = self.model.generate_content(prompt, stream=True)

        for chunk in response:
            if chunk.text:
                yield chunk.text
