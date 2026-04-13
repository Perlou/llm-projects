"""
图表分析器
==========

使用 Gemini 分析各类图表，提取数据和洞察。

支持图表类型:
    - 折线图
    - 柱状图
    - 饼图
    - 散点图
    - 热力图
    - 组合图表
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

import google.generativeai as genai
from PIL import Image

from config import config


@dataclass
class ChartAnalysisResult:
    """图表分析结果"""

    chart_type: str = ""
    title: str = ""
    data: List[Dict[str, Any]] = field(default_factory=list)
    x_axis: Dict[str, Any] = field(default_factory=dict)
    y_axis: Dict[str, Any] = field(default_factory=dict)
    legend: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    trend: str = ""
    raw_response: str = ""


class ChartAnalyzer:
    """图表分析器"""

    def __init__(self, model_name: Optional[str] = None):
        """
        初始化图表分析器

        Args:
            model_name: Gemini 模型名称
        """
        genai.configure(api_key=config.google_api_key)
        self.model = genai.GenerativeModel(model_name or config.gemini_model)

    def _load_image(self, image_source: Union[str, Path, Image.Image]) -> Image.Image:
        """加载图像"""
        if isinstance(image_source, Image.Image):
            return image_source
        return Image.open(image_source)

    def _resize_if_needed(self, image: Image.Image) -> Image.Image:
        """如果图像过大则缩放"""
        max_size = config.max_image_size
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        return image

    def analyze(
        self,
        image_source: Union[str, Path, Image.Image],
        extract_data: bool = True,
    ) -> ChartAnalysisResult:
        """
        分析图表，识别类型并提取信息

        Args:
            image_source: 图表图片路径或 PIL Image 对象
            extract_data: 是否提取详细数据点

        Returns:
            ChartAnalysisResult: 分析结果
        """
        image = self._load_image(image_source)
        image = self._resize_if_needed(image)

        prompt = """分析这张图表，返回 JSON 格式：

{
    "chart_type": "图表类型（折线图/柱状图/饼图/散点图/热力图/组合图等）",
    "title": "图表标题",
    "x_axis": {
        "label": "X轴标签",
        "type": "数据类型（数值/分类/时间）",
        "range": "范围或类别列表"
    },
    "y_axis": {
        "label": "Y轴标签",
        "type": "数据类型",
        "range": "数值范围"
    },
    "legend": ["图例项列表"],
    "data": [
        {"label": "标签", "value": 数值, "series": "系列名（如有）"}
    ],
    "statistics": {
        "max": {"label": "最大值标签", "value": 最大值},
        "min": {"label": "最小值标签", "value": 最小值},
        "average": 平均值
    },
    "trend": "整体趋势描述",
    "insights": ["关键发现列表"]
}

尽可能精确读取数值，如无法确定给出估计值。只返回 JSON。"""

        response = self.model.generate_content([prompt, image])

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)

            return ChartAnalysisResult(
                chart_type=data.get("chart_type", ""),
                title=data.get("title", ""),
                data=data.get("data", []),
                x_axis=data.get("x_axis", {}),
                y_axis=data.get("y_axis", {}),
                legend=data.get("legend", []),
                statistics=data.get("statistics", {}),
                insights=data.get("insights", []),
                trend=data.get("trend", ""),
                raw_response=response.text,
            )
        except json.JSONDecodeError:
            return ChartAnalysisResult(raw_response=response.text)

    def extract_data(
        self,
        image_source: Union[str, Path, Image.Image],
        output_format: str = "json",
    ) -> Union[List[Dict], str]:
        """
        从图表中提取数据

        Args:
            image_source: 图表图片
            output_format: 输出格式 ("json", "csv", "markdown")

        Returns:
            提取的数据
        """
        image = self._load_image(image_source)
        image = self._resize_if_needed(image)

        format_prompts = {
            "json": "以 JSON 数组格式返回",
            "csv": "以 CSV 格式返回（包含表头）",
            "markdown": "以 Markdown 表格格式返回",
        }

        prompt = f"""从这张图表中提取所有可读的数据点。

{format_prompts.get(output_format, format_prompts["json"])}

要求：
1. 精确读取每个数据点
2. 保持原始数据结构
3. 如果有多个系列，区分显示
4. 只返回数据，不要其他说明"""

        response = self.model.generate_content([prompt, image])

        if output_format == "json":
            try:
                text = response.text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                return json.loads(text)
            except json.JSONDecodeError:
                return []
        else:
            return response.text

    def analyze_trend(
        self,
        image_source: Union[str, Path, Image.Image],
        context: str = "",
    ) -> str:
        """
        分析图表趋势并生成洞察

        Args:
            image_source: 图表图片
            context: 背景信息

        Returns:
            趋势分析报告
        """
        image = self._load_image(image_source)
        image = self._resize_if_needed(image)

        prompt = f"""分析这张图表的趋势，提供专业的数据分析洞察。

背景信息：{context if context else "无"}

请从以下方面分析：
1. 整体趋势（上升/下降/平稳/波动）
2. 关键转折点
3. 异常值或特殊点
4. 周期性模式（如有）
5. 与预期的对比（如有背景信息）
6. 可能的原因分析
7. 未来趋势预测
8. 行动建议

用专业但易懂的中文回答。"""

        response = self.model.generate_content([prompt, image])
        return response.text

    def compare_charts(
        self,
        images: List[Union[str, Path, Image.Image]],
        analysis_focus: str = "",
    ) -> str:
        """
        对比分析多个图表

        Args:
            images: 图表图片列表
            analysis_focus: 分析重点

        Returns:
            对比分析报告
        """
        loaded_images = []
        for img in images:
            image = self._load_image(img)
            image = self._resize_if_needed(image)
            loaded_images.append(image)

        prompt = f"""对比分析以下{len(images)}张图表。

分析重点：{analysis_focus if analysis_focus else "全面对比"}

请从以下方面进行对比：
1. 数据范围和规模对比
2. 趋势一致性或差异
3. 相关性分析
4. 共同模式发现
5. 差异点及可能原因
6. 综合结论和建议

用中文回答。"""

        content = [prompt] + loaded_images
        response = self.model.generate_content(content)
        return response.text

    def generate_report(
        self,
        image_source: Union[str, Path, Image.Image],
        report_type: str = "summary",
    ) -> str:
        """
        生成图表分析报告

        Args:
            image_source: 图表图片
            report_type: 报告类型 ("summary", "detailed", "executive")

        Returns:
            分析报告
        """
        image = self._load_image(image_source)
        image = self._resize_if_needed(image)

        type_prompts = {
            "summary": "生成简洁的摘要报告（3-5段）",
            "detailed": "生成详细的分析报告（包含所有数据和分析）",
            "executive": "生成管理层摘要（关键指标和建议）",
        }

        prompt = f"""基于这张图表，{type_prompts.get(report_type, type_prompts["summary"])}。

报告结构：
1. 概述
2. 关键发现
3. 数据分析
4. 趋势判断
5. 建议措施

用专业的中文撰写。"""

        response = self.model.generate_content([prompt, image])
        return response.text
