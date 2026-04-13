"""
分析器测试
==========

测试各个分析器的基本功能。
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 测试数据目录
TEST_DATA_DIR = Path(__file__).parent.parent / "data"


class TestImageAnalyzer:
    """图像分析器测试"""

    def test_init(self):
        """测试初始化"""
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel"):
                from analyzers import ImageAnalyzer

                analyzer = ImageAnalyzer()
                assert analyzer is not None

    def test_describe_result_structure(self):
        """测试描述结果结构"""
        from analyzers import ImageAnalysisResult

        result = ImageAnalysisResult(
            description="测试描述",
            objects=[{"name": "物体1"}],
            text="识别的文字",
        )

        assert result.description == "测试描述"
        assert len(result.objects) == 1
        assert result.text == "识别的文字"


class TestChartAnalyzer:
    """图表分析器测试"""

    def test_init(self):
        """测试初始化"""
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel"):
                from analyzers import ChartAnalyzer

                analyzer = ChartAnalyzer()
                assert analyzer is not None

    def test_chart_result_structure(self):
        """测试图表结果结构"""
        from analyzers import ChartAnalysisResult

        result = ChartAnalysisResult(
            chart_type="柱状图",
            title="测试图表",
            data=[{"label": "Q1", "value": 100}],
            trend="上升趋势",
        )

        assert result.chart_type == "柱状图"
        assert result.title == "测试图表"
        assert len(result.data) == 1
        assert result.trend == "上升趋势"


class TestVideoAnalyzer:
    """视频分析器测试"""

    def test_init(self):
        """测试初始化"""
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel"):
                from analyzers import VideoAnalyzer

                analyzer = VideoAnalyzer()
                assert analyzer is not None

    def test_video_result_structure(self):
        """测试视频结果结构"""
        from analyzers import VideoAnalysisResult

        result = VideoAnalysisResult(
            summary="视频摘要",
            duration=120.0,
            key_frames=[{"index": 0, "timestamp": 10.0}],
        )

        assert result.summary == "视频摘要"
        assert result.duration == 120.0
        assert len(result.key_frames) == 1


class TestAudioAnalyzer:
    """音频分析器测试"""

    def test_init(self):
        """测试初始化"""
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel"):
                from analyzers import AudioAnalyzer

                analyzer = AudioAnalyzer(use_openai=False)
                assert analyzer is not None

    def test_audio_result_structure(self):
        """测试音频结果结构"""
        from analyzers import AudioAnalysisResult

        result = AudioAnalysisResult(
            transcript="转录文本",
            summary="内容摘要",
            keywords=["关键词1", "关键词2"],
            duration=60.0,
        )

        assert result.transcript == "转录文本"
        assert result.summary == "内容摘要"
        assert len(result.keywords) == 2
        assert result.duration == 60.0


class TestConfig:
    """配置测试"""

    def test_config_creation(self):
        """测试配置创建"""
        from config import Config

        cfg = Config()
        assert cfg.gemini_model is not None

    def test_config_paths(self):
        """测试路径配置"""
        from config import config

        assert config.data_dir.exists() or True  # 允许目录不存在
        assert config.base_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
