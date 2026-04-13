"""
音频分析器
==========

音频转录和内容分析。

支持功能:
    - 语音转文字
    - 内容摘要
    - 关键词提取
    - 会议分析

注意:
    Gemini SDK 当前不直接支持音频输入。
    本模块使用以下方案:
    1. 如果有 OpenAI API Key，使用 Whisper
    2. 否则使用本地 SpeechRecognition
"""

import json
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

import google.generativeai as genai

from config import config

# 尝试导入音频处理库
try:
    from pydub import AudioSegment

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None

# 尝试导入 OpenAI (用于 Whisper)
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

# 尝试导入 SpeechRecognition
try:
    import speech_recognition as sr

    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    sr = None


@dataclass
class AudioAnalysisResult:
    """音频分析结果"""

    transcript: str = ""
    summary: str = ""
    keywords: List[str] = field(default_factory=list)
    speakers: List[Dict[str, Any]] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    duration: float = 0.0
    language: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class AudioAnalyzer:
    """音频分析器"""

    def __init__(self, use_openai: bool = True):
        """
        初始化音频分析器

        Args:
            use_openai: 是否使用 OpenAI Whisper（如果可用）
        """
        genai.configure(api_key=config.google_api_key)
        self.gemini = genai.GenerativeModel(config.gemini_model)

        self.use_openai = use_openai and OPENAI_AVAILABLE and config.openai_api_key
        if self.use_openai:
            self.openai = OpenAI(api_key=config.openai_api_key)

        if not PYDUB_AVAILABLE:
            print("⚠️  警告: pydub 未安装，音频处理功能有限")
            print("   安装: pip install pydub")

    def _get_audio_duration(self, audio_path: Union[str, Path]) -> float:
        """获取音频时长（秒）"""
        if not PYDUB_AVAILABLE:
            return 0.0
        audio = AudioSegment.from_file(str(audio_path))
        return len(audio) / 1000.0

    def _convert_to_wav(self, audio_path: Union[str, Path]) -> str:
        """转换音频为 WAV 格式"""
        if not PYDUB_AVAILABLE:
            return str(audio_path)

        audio = AudioSegment.from_file(str(audio_path))
        temp_path = tempfile.mktemp(suffix=".wav")
        audio.export(temp_path, format="wav")
        return temp_path

    def transcribe(
        self,
        audio_path: Union[str, Path],
        language: str = "zh",
    ) -> AudioAnalysisResult:
        """
        语音转文字

        Args:
            audio_path: 音频文件路径
            language: 语言代码 ("zh", "en" 等)

        Returns:
            AudioAnalysisResult: 转录结果
        """
        audio_path = str(audio_path)
        duration = self._get_audio_duration(audio_path)

        # 方案 1: 使用 OpenAI Whisper
        if self.use_openai:
            try:
                with open(audio_path, "rb") as audio_file:
                    response = self.openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language,
                        response_format="text",
                    )
                transcript = response

                return AudioAnalysisResult(
                    transcript=transcript,
                    duration=duration,
                    language=language,
                    metadata={"method": "whisper"},
                )
            except Exception as e:
                print(f"⚠️  Whisper 转录失败: {e}")

        # 方案 2: 使用 SpeechRecognition
        if SR_AVAILABLE:
            try:
                wav_path = self._convert_to_wav(audio_path)
                recognizer = sr.Recognizer()

                with sr.AudioFile(wav_path) as source:
                    audio_data = recognizer.record(source)

                # 使用 Google Speech Recognition（免费但有限制）
                transcript = recognizer.recognize_google(
                    audio_data,
                    language=f"{language}-CN" if language == "zh" else language,
                )

                return AudioAnalysisResult(
                    transcript=transcript,
                    duration=duration,
                    language=language,
                    metadata={"method": "google_speech"},
                )
            except Exception as e:
                print(f"⚠️  SpeechRecognition 转录失败: {e}")

        # 如果都不可用
        return AudioAnalysisResult(
            transcript="[音频转录不可用，请安装 openai 或 SpeechRecognition]",
            duration=duration,
            metadata={"method": "unavailable"},
        )

    def analyze(
        self,
        audio_path: Union[str, Path],
        language: str = "zh",
    ) -> AudioAnalysisResult:
        """
        转录并分析音频内容

        Args:
            audio_path: 音频文件路径
            language: 语言代码

        Returns:
            AudioAnalysisResult: 完整分析结果
        """
        # 先转录
        result = self.transcribe(audio_path, language)

        if not result.transcript or result.transcript.startswith("["):
            return result

        # 使用 Gemini 分析转录文本
        prompt = f"""分析以下音频转录文本：

---
{result.transcript}
---

返回 JSON 格式：
{{
    "summary": "内容摘要（2-3句话）",
    "keywords": ["关键词列表"],
    "topics": ["讨论的主题"],
    "speakers_detected": 检测到的说话人数（估计）,
    "tone": "整体语气（正式/非正式/严肃/轻松等）",
    "type": "内容类型（会议/采访/讲座/对话等）"
}}

只返回 JSON。"""

        response = self.gemini.generate_content(prompt)

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)

            result.summary = data.get("summary", "")
            result.keywords = data.get("keywords", [])
            result.topics = data.get("topics", [])
            result.metadata.update(data)

        except json.JSONDecodeError:
            result.summary = response.text

        return result

    def meeting_analysis(
        self,
        audio_path: Union[str, Path],
        language: str = "zh",
    ) -> AudioAnalysisResult:
        """
        会议录音分析

        Args:
            audio_path: 会议录音文件路径
            language: 语言代码

        Returns:
            AudioAnalysisResult: 会议分析结果
        """
        # 先转录
        result = self.transcribe(audio_path, language)

        if not result.transcript or result.transcript.startswith("["):
            return result

        # 使用 Gemini 进行会议分析
        prompt = f"""分析以下会议记录：

---
{result.transcript}
---

返回 JSON 格式：
{{
    "summary": "会议摘要（3-5句话）",
    "key_decisions": ["关键决策列表"],
    "action_items": [
        {{"task": "任务描述", "assignee": "负责人（如能识别）", "deadline": "截止日期（如有提及）"}}
    ],
    "topics_discussed": ["讨论的话题"],
    "open_questions": ["未解决的问题"],
    "next_steps": ["下一步计划"],
    "participants_count": 参与人数估计
}}

只返回 JSON。"""

        response = self.gemini.generate_content(prompt)

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)

            result.summary = data.get("summary", "")
            result.action_items = [
                item.get("task", str(item)) for item in data.get("action_items", [])
            ]
            result.topics = data.get("topics_discussed", [])
            result.metadata.update(data)

        except json.JSONDecodeError:
            result.summary = response.text

        return result

    def extract_text_with_timestamps(
        self,
        audio_path: Union[str, Path],
        language: str = "zh",
    ) -> List[Dict[str, Any]]:
        """
        提取带时间戳的转录

        Args:
            audio_path: 音频文件路径
            language: 语言代码

        Returns:
            带时间戳的转录段落列表
        """
        if not self.use_openai:
            return [
                {"text": "需要 OpenAI API Key 才能使用时间戳功能", "start": 0, "end": 0}
            ]

        try:
            with open(str(audio_path), "rb") as audio_file:
                response = self.openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                )

            segments = []
            for segment in response.segments:
                segments.append(
                    {
                        "text": segment.text,
                        "start": segment.start,
                        "end": segment.end,
                        "start_str": f"{int(segment.start // 60):02d}:{int(segment.start % 60):02d}",
                        "end_str": f"{int(segment.end // 60):02d}:{int(segment.end % 60):02d}",
                    }
                )

            return segments

        except Exception as e:
            return [{"text": f"转录失败: {e}", "start": 0, "end": 0}]
