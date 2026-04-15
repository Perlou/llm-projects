"""
测试用例
========

服务层测试。
"""

import pytest
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfig:
    """配置测试"""

    def test_config_import(self):
        """测试配置导入"""
        from config import config

        assert config is not None

    def test_model_info(self):
        """测试模型信息"""
        from config import config

        info = config.get_model_info()
        assert "Gemini" in info or "Ollama" in info


class TestLLMProvider:
    """LLM 提供者测试"""

    def test_get_provider(self):
        """测试获取提供者"""
        from services.llm_provider import get_provider

        provider = get_provider()
        assert provider is not None

    def test_get_llm(self):
        """测试获取 LLM"""
        from services.llm_provider import get_llm

        llm = get_llm()
        assert llm is not None


class TestKnowledgeBase:
    """知识库测试"""

    def test_create_and_delete(self):
        """测试创建和删除知识库"""
        from services.knowledge_base import get_kb_manager

        manager = get_kb_manager()

        # 创建
        kb = manager.create_knowledge_base("测试知识库", "测试用")
        assert kb is not None
        assert kb.name == "测试知识库"

        # 获取
        retrieved = manager.get_knowledge_base(kb.id)
        assert retrieved is not None
        assert retrieved.id == kb.id

        # 删除
        success = manager.delete_knowledge_base(kb.id)
        assert success

        # 验证删除
        deleted = manager.get_knowledge_base(kb.id)
        assert deleted is None


class TestChatService:
    """对话服务测试"""

    def test_create_session(self):
        """测试创建会话"""
        from services.chat import get_chat_service

        service = get_chat_service()
        session = service.create_session()

        assert session is not None
        assert session.id is not None

    def test_list_sessions(self):
        """测试列出会话"""
        from services.chat import get_chat_service

        service = get_chat_service()
        service.create_session()

        sessions = service.list_sessions()
        assert len(sessions) > 0


class TestModules:
    """模块测试"""

    def test_qa_module(self):
        """测试 QA 模块"""
        from modules.qa import QAModule

        qa = QAModule()
        assert qa is not None

    def test_document_processor(self):
        """测试文档处理器"""
        from modules.document import DocumentProcessor

        processor = DocumentProcessor()
        assert processor is not None

    def test_content_creator(self):
        """测试内容创作器"""
        from modules.content import ContentCreator

        creator = ContentCreator()
        assert creator is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
