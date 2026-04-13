"""
图像分析器
==========

使用 Gemini 进行图像内容理解和分析。

支持功能:
    - 图像内容描述
    - 物体检测
    - 文字识别 (OCR)
    - 场景理解
"""

import base64
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

import google.generativeai as genai
from PIL import Image

from config import config


@dataclass
class ImageAnalysisResult:
    """图像分析结果"""

    description: str = ""
    objects: List[Dict[str, Any]] = field(default_factory=list)
    text: str = ""
    scene: str = ""
    colors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: str = ""


class ImageAnalyzer:
    """图像分析器"""

    def __init__(self, model_name: Optional[str] = None):
        """
        初始化图像分析器

        Args:
            model_name: Gemini 模型名称，默认使用配置中的模型
        """
        genai.configure(api_key=config.google_api_key)
        self.model = genai.GenerativeModel(model_name or config.gemini_model)

    def _load_image(self, image_source: Union[str, Path, Image.Image]) -> Image.Image:
        """加载图像"""
        if isinstance(image_source, Image.Image):
            return image_source
        return Image.open(image_source)

    def _resize_if_needed(self, image: Image.Image) -> Image.Image:
        """
        如果图像过大则缩放

        Gemini API 对图像大小有限制，需要适当缩放
        """
        max_size = config.max_image_size
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        return image

    def describe(
        self,
        image_source: Union[str, Path, Image.Image],
        detail_level: str = "detailed",
        language: str = "zh",
    ) -> ImageAnalysisResult:
        """
        描述图像内容

        Args:
            image_source: 图像路径或 PIL Image 对象
            detail_level: 描述详细程度 ("brief", "detailed", "comprehensive")
            language: 输出语言 ("zh", "en")

        Returns:
            ImageAnalysisResult: 分析结果
        """
        image = self._load_image(image_source)
        image = self._resize_if_needed(image)

        detail_prompts = {
            "brief": "用一两句话简要描述这张图片的内容。",
            "detailed": "详细描述这张图片的内容，包括主要元素、场景、颜色和氛围。",
            "comprehensive": """全面分析这张图片，包括：
1. 主要内容描述
2. 场景和环境
3. 主要物体和位置
4. 颜色和光线
5. 情感和氛围
6. 可能的拍摄意图或背景""",
        }

        lang_prompt = (
            "请用中文回答。" if language == "zh" else "Please respond in English."
        )
        prompt = f"{detail_prompts.get(detail_level, detail_prompts['detailed'])}\n{lang_prompt}"

        response = self.model.generate_content([prompt, image])

        return ImageAnalysisResult(
            description=response.text,
            raw_response=response.text,
            metadata={"detail_level": detail_level, "language": language},
        )

    def detect_objects(
        self,
        image_source: Union[str, Path, Image.Image],
    ) -> ImageAnalysisResult:
        """
        检测图像中的物体

        Args:
            image_source: 图像路径或 PIL Image 对象

        Returns:
            ImageAnalysisResult: 包含检测到的物体列表
        """
        image = self._load_image(image_source)
        image = self._resize_if_needed(image)

        prompt = """分析这张图片中的所有物体，返回 JSON 格式：

{
    "objects": [
        {
            "name": "物体名称",
            "category": "类别（人物/动物/物品/建筑/自然等）",
            "position": "位置描述（左上/中央/右下等）",
            "confidence": "确信度（高/中/低）",
            "attributes": ["属性1", "属性2"]
        }
    ],
    "total_count": 物体总数,
    "main_subject": "画面主体"
}

只返回 JSON，不要其他文字。"""

        response = self.model.generate_content([prompt, image])

        try:
            # 清理响应，提取 JSON
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)
            objects = data.get("objects", [])
        except json.JSONDecodeError:
            objects = []

        return ImageAnalysisResult(
            objects=objects,
            raw_response=response.text,
        )

    def extract_text(
        self,
        image_source: Union[str, Path, Image.Image],
        structured: bool = False,
    ) -> ImageAnalysisResult:
        """
        从图像中提取文字 (OCR)

        Args:
            image_source: 图像路径或 PIL Image 对象
            structured: 是否返回结构化数据（位置信息等）

        Returns:
            ImageAnalysisResult: 包含提取的文字
        """
        image = self._load_image(image_source)
        image = self._resize_if_needed(image)

        if structured:
            prompt = """提取这张图片中的所有文字，返回 JSON 格式：

{
    "text_blocks": [
        {
            "text": "文字内容",
            "type": "类型（标题/正文/标签/按钮等）",
            "position": "位置",
            "language": "语言"
        }
    ],
    "full_text": "所有文字的完整内容",
    "language": "主要语言"
}

只返回 JSON，不要其他文字。"""
        else:
            prompt = "请提取这张图片中的所有文字内容，保持原有格式和布局。只返回提取到的文字，不要其他说明。"

        response = self.model.generate_content([prompt, image])

        text = response.text.strip()
        if structured:
            try:
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                data = json.loads(text)
                extracted_text = data.get("full_text", "")
            except json.JSONDecodeError:
                extracted_text = text
        else:
            extracted_text = text

        return ImageAnalysisResult(
            text=extracted_text,
            raw_response=response.text,
        )

    def analyze_scene(
        self,
        image_source: Union[str, Path, Image.Image],
    ) -> ImageAnalysisResult:
        """
        分析图像场景

        Args:
            image_source: 图像路径或 PIL Image 对象

        Returns:
            ImageAnalysisResult: 包含场景分析结果
        """
        image = self._load_image(image_source)
        image = self._resize_if_needed(image)

        prompt = """分析这张图片的场景，返回 JSON 格式：

{
    "scene_type": "场景类型（室内/室外/自然/城市等）",
    "location": "可能的地点描述",
    "time_of_day": "时间推断（白天/夜晚/黄昏等）",
    "weather": "天气（如适用）",
    "atmosphere": "氛围（热闹/宁静/紧张等）",
    "colors": {
        "dominant": ["主色调列表"],
        "accent": ["点缀色列表"]
    },
    "style": "风格（写实/艺术/复古等）"
}

只返回 JSON，不要其他文字。"""

        response = self.model.generate_content([prompt, image])

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)
            scene = data.get("scene_type", "")
            colors = data.get("colors", {}).get("dominant", [])
        except json.JSONDecodeError:
            scene = ""
            colors = []

        return ImageAnalysisResult(
            scene=scene,
            colors=colors,
            raw_response=response.text,
        )

    def analyze_full(
        self,
        image_source: Union[str, Path, Image.Image],
    ) -> ImageAnalysisResult:
        """
        执行完整分析（组合多个分析任务）

        Args:
            image_source: 图像路径或 PIL Image 对象

        Returns:
            ImageAnalysisResult: 完整分析结果
        """
        image = self._load_image(image_source)
        image = self._resize_if_needed(image)

        prompt = """对这张图片进行全面分析，返回 JSON 格式：

{
    "description": "详细的图片描述",
    "scene": {
        "type": "场景类型",
        "location": "地点",
        "atmosphere": "氛围"
    },
    "objects": [
        {
            "name": "物体名称",
            "category": "类别",
            "position": "位置"
        }
    ],
    "text": "图片中的文字（如有）",
    "colors": ["主要颜色"],
    "style": "图片风格",
    "insights": "额外洞察或有趣的观察"
}

只返回 JSON，不要其他文字。"""

        response = self.model.generate_content([prompt, image])

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)

            return ImageAnalysisResult(
                description=data.get("description", ""),
                objects=data.get("objects", []),
                text=data.get("text", ""),
                scene=data.get("scene", {}).get("type", ""),
                colors=data.get("colors", []),
                metadata=data,
                raw_response=response.text,
            )
        except json.JSONDecodeError:
            return ImageAnalysisResult(
                description=response.text,
                raw_response=response.text,
            )
