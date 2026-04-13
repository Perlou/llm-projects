"""
配置管理
========

集中管理应用配置，支持环境变量覆盖。
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class Config:
    """应用配置"""

    # API 配置
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )

    # 模型配置
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    )

    # 路径配置
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent)

    @property
    def data_dir(self) -> Path:
        """数据目录"""
        path = self.base_dir / os.getenv("DATA_DIR", "data")
        path.mkdir(exist_ok=True)
        return path

    @property
    def images_dir(self) -> Path:
        """图片目录"""
        path = self.data_dir / "images"
        path.mkdir(exist_ok=True)
        return path

    @property
    def videos_dir(self) -> Path:
        """视频目录"""
        path = self.data_dir / "videos"
        path.mkdir(exist_ok=True)
        return path

    @property
    def audio_dir(self) -> Path:
        """音频目录"""
        path = self.data_dir / "audio"
        path.mkdir(exist_ok=True)
        return path

    @property
    def vector_store_dir(self) -> Path:
        """向量存储目录"""
        path = self.base_dir / os.getenv("VECTOR_STORE_DIR", "chroma_db")
        path.mkdir(exist_ok=True)
        return path

    # 处理配置
    max_image_size: int = field(
        default_factory=lambda: int(os.getenv("MAX_IMAGE_SIZE", "4096"))
    )
    max_video_frames: int = field(
        default_factory=lambda: int(os.getenv("MAX_VIDEO_FRAMES", "30"))
    )

    def validate(self) -> bool:
        """验证配置"""
        if not self.google_api_key:
            print("❌ 错误: 请设置 GOOGLE_API_KEY 环境变量")
            print("   获取地址: https://aistudio.google.com/apikey")
            return False
        return True


# 全局配置实例
config = Config()
