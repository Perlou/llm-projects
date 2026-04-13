"""
视频分析器
==========

使用 Gemini 进行视频内容理解和摘要。

支持功能:
    - 视频内容摘要
    - 关键帧提取和分析
    - 视频问答
    - 场景分割
"""

import json
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

import google.generativeai as genai
from PIL import Image

from config import config

# 尝试导入 moviepy，如果不可用则使用备用方案
try:
    from moviepy import VideoFileClip

    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    VideoFileClip = None


@dataclass
class VideoAnalysisResult:
    """视频分析结果"""

    summary: str = ""
    key_frames: List[Dict[str, Any]] = field(default_factory=list)
    timestamps: List[Dict[str, Any]] = field(default_factory=list)
    duration: float = 0.0
    scenes: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: str = ""


class VideoAnalyzer:
    """视频分析器"""

    def __init__(self, model_name: Optional[str] = None):
        """
        初始化视频分析器

        Args:
            model_name: Gemini 模型名称
        """
        genai.configure(api_key=config.google_api_key)
        self.model = genai.GenerativeModel(model_name or config.gemini_model)
        self.max_frames = config.max_video_frames

        if not MOVIEPY_AVAILABLE:
            print("⚠️  警告: moviepy 未安装，视频处理功能有限")
            print("   安装: pip install moviepy")

    def _extract_frames(
        self,
        video_path: Union[str, Path],
        num_frames: int = 10,
    ) -> List[Image.Image]:
        """
        从视频中提取关键帧

        Args:
            video_path: 视频文件路径
            num_frames: 要提取的帧数

        Returns:
            帧图像列表
        """
        if not MOVIEPY_AVAILABLE:
            raise RuntimeError("需要安装 moviepy: pip install moviepy")

        video_path = str(video_path)
        clip = VideoFileClip(video_path)
        duration = clip.duration

        # 计算采样时间点
        if num_frames > self.max_frames:
            num_frames = self.max_frames

        interval = duration / (num_frames + 1)
        timestamps = [interval * (i + 1) for i in range(num_frames)]

        frames = []
        for t in timestamps:
            frame = clip.get_frame(t)
            image = Image.fromarray(frame)
            frames.append(image)

        clip.close()
        return frames

    def _get_video_info(self, video_path: Union[str, Path]) -> Dict[str, Any]:
        """获取视频基本信息"""
        if not MOVIEPY_AVAILABLE:
            return {}

        video_path = str(video_path)
        clip = VideoFileClip(video_path)

        info = {
            "duration": clip.duration,
            "fps": clip.fps,
            "size": clip.size,
            "width": clip.size[0],
            "height": clip.size[1],
        }

        clip.close()
        return info

    def summarize(
        self,
        video_path: Union[str, Path],
        num_frames: int = 10,
        detail_level: str = "detailed",
    ) -> VideoAnalysisResult:
        """
        生成视频摘要

        Args:
            video_path: 视频文件路径
            num_frames: 分析的帧数
            detail_level: 详细程度 ("brief", "detailed", "comprehensive")

        Returns:
            VideoAnalysisResult: 分析结果
        """
        # 获取视频信息
        video_info = self._get_video_info(video_path)

        # 提取关键帧
        frames = self._extract_frames(video_path, num_frames)

        detail_prompts = {
            "brief": "用一段话简要概括",
            "detailed": "详细描述，包括主要内容、场景变化、关键时刻",
            "comprehensive": "全面分析，包括内容、风格、制作、目标受众等",
        }

        prompt = f"""这是从一个视频中均匀采样的{len(frames)}帧画面。
视频时长约{video_info.get("duration", 0):.1f}秒。

请{detail_prompts.get(detail_level, detail_prompts["detailed"])}这个视频的内容。

返回 JSON 格式：
{{
    "summary": "视频整体摘要",
    "scenes": [
        {{"description": "场景描述", "estimated_time": "估计时间范围"}}
    ],
    "key_moments": ["关键时刻描述"],
    "content_type": "内容类型（教程/娱乐/新闻/广告等）",
    "tone": "整体风格/基调",
    "main_subjects": ["主要主体"]
}}

只返回 JSON。"""

        content = [prompt] + frames
        response = self.model.generate_content(content)

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)

            # 构建关键帧信息
            key_frames = []
            for i, frame in enumerate(frames):
                interval = video_info.get("duration", 0) / (len(frames) + 1)
                timestamp = interval * (i + 1)
                key_frames.append(
                    {
                        "index": i,
                        "timestamp": timestamp,
                        "timestamp_str": f"{int(timestamp // 60):02d}:{int(timestamp % 60):02d}",
                    }
                )

            return VideoAnalysisResult(
                summary=data.get("summary", ""),
                key_frames=key_frames,
                scenes=data.get("scenes", []),
                duration=video_info.get("duration", 0),
                metadata=data,
                raw_response=response.text,
            )
        except json.JSONDecodeError:
            return VideoAnalysisResult(
                summary=response.text,
                duration=video_info.get("duration", 0),
                raw_response=response.text,
            )

    def analyze_frames(
        self,
        video_path: Union[str, Path],
        num_frames: int = 10,
    ) -> VideoAnalysisResult:
        """
        分析视频的每一帧

        Args:
            video_path: 视频文件路径
            num_frames: 分析的帧数

        Returns:
            包含每帧分析结果
        """
        video_info = self._get_video_info(video_path)
        frames = self._extract_frames(video_path, num_frames)

        prompt = f"""分析这{len(frames)}帧视频画面，描述每一帧的内容。

返回 JSON 格式：
{{
    "frames": [
        {{
            "index": 帧序号,
            "description": "该帧内容描述",
            "objects": ["检测到的物体"],
            "text": "画面中的文字（如有）",
            "action": "正在发生的动作"
        }}
    ],
    "narrative": "整体叙事描述",
    "transitions": ["场景转换描述"]
}}

只返回 JSON。"""

        content = [prompt] + frames
        response = self.model.generate_content(content)

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)

            # 添加时间戳
            frame_data = data.get("frames", [])
            for i, frame_info in enumerate(frame_data):
                interval = video_info.get("duration", 0) / (len(frames) + 1)
                timestamp = interval * (i + 1)
                frame_info["timestamp"] = timestamp
                frame_info["timestamp_str"] = (
                    f"{int(timestamp // 60):02d}:{int(timestamp % 60):02d}"
                )

            return VideoAnalysisResult(
                key_frames=frame_data,
                summary=data.get("narrative", ""),
                duration=video_info.get("duration", 0),
                metadata=data,
                raw_response=response.text,
            )
        except json.JSONDecodeError:
            return VideoAnalysisResult(
                summary=response.text,
                raw_response=response.text,
            )

    def answer_question(
        self,
        video_path: Union[str, Path],
        question: str,
        num_frames: int = 10,
    ) -> str:
        """
        回答关于视频的问题

        Args:
            video_path: 视频文件路径
            question: 用户问题
            num_frames: 分析的帧数

        Returns:
            答案文本
        """
        frames = self._extract_frames(video_path, num_frames)

        prompt = f"""这是从一个视频中采样的{len(frames)}帧画面。

请根据视频内容回答以下问题：
{question}

用中文详细回答。"""

        content = [prompt] + frames
        response = self.model.generate_content(content)
        return response.text

    def detect_scenes(
        self,
        video_path: Union[str, Path],
        num_frames: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        检测视频中的场景分割

        Args:
            video_path: 视频文件路径
            num_frames: 分析的帧数（越多越精确）

        Returns:
            场景列表
        """
        video_info = self._get_video_info(video_path)
        frames = self._extract_frames(video_path, num_frames)

        prompt = f"""分析这{len(frames)}帧，识别视频中的不同场景（场景切换点）。

视频总时长约{video_info.get("duration", 0):.1f}秒，这些帧是均匀采样的。

返回 JSON 格式：
{{
    "scenes": [
        {{
            "scene_id": 场景编号,
            "start_frame": 开始帧索引,
            "end_frame": 结束帧索引,
            "description": "场景描述",
            "type": "场景类型"
        }}
    ],
    "total_scenes": 总场景数,
    "transitions": ["转场方式（切换/淡入淡出等）"]
}}

只返回 JSON。"""

        content = [prompt] + frames
        response = self.model.generate_content(content)

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)

            # 添加时间估算
            scenes = data.get("scenes", [])
            for scene in scenes:
                start_idx = scene.get("start_frame", 0)
                end_idx = scene.get("end_frame", 0)
                interval = video_info.get("duration", 0) / (len(frames) + 1)
                scene["start_time"] = interval * (start_idx + 1)
                scene["end_time"] = interval * (end_idx + 1)

            return scenes
        except json.JSONDecodeError:
            return []
