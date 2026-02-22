"""
测试文档加载器
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_loader import DocumentLoader


class TestDocumentLoader:
    """文档加载器测试"""

    def test_load_txt_file(self):
        """测试加载 TXT 文件"""
        loader = DocumentLoader()

        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("这是测试内容。\n这是第二行。")
            temp_path = f.name

        try:
            result = loader.load_file(temp_path)

            assert result.filename.endswith(".txt")
            assert result.file_type == "Text"
            assert len(result.documents) >= 1
            assert "这是测试内容" in result.documents[0].page_content
        finally:
            os.unlink(temp_path)

    def test_load_md_file(self):
        """测试加载 Markdown 文件"""
        loader = DocumentLoader()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("# 标题\n\n这是正文内容。")
            temp_path = f.name

        try:
            result = loader.load_file(temp_path)

            assert result.file_type == "Markdown"
            assert len(result.documents) >= 1
        finally:
            os.unlink(temp_path)

    def test_unsupported_format(self):
        """测试不支持的文件格式"""
        loader = DocumentLoader()

        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="不支持的文件格式"):
                loader.load_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_file_not_found(self):
        """测试文件不存在"""
        loader = DocumentLoader()

        with pytest.raises(FileNotFoundError):
            loader.load_file("/nonexistent/path/file.txt")

    def test_get_all_documents(self):
        """测试获取所有文档"""
        loader = DocumentLoader()

        # 创建两个临时文件
        temp_files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as f:
                f.write(f"测试内容 {i}")
                temp_files.append(f.name)

        try:
            for path in temp_files:
                loader.load_file(path)

            all_docs = loader.get_all_documents()
            assert len(all_docs) == 2
        finally:
            for path in temp_files:
                os.unlink(path)

    def test_get_stats(self):
        """测试获取统计信息"""
        loader = DocumentLoader()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("测试内容")
            temp_path = f.name

        try:
            loader.load_file(temp_path)
            stats = loader.get_stats()

            assert stats["total_files"] == 1
            assert len(stats["files"]) == 1
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
