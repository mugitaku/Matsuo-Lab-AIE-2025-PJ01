import pytest
from unittest.mock import Mock, patch

from src.response_engine.qa_engine import QAEngine, ResponseMode
from src.response_engine.hint_generator import HintGenerator, HintLevel


class TestQAEngine:
    """QAEngineのテスト"""
    
    @pytest.fixture
    def qa_engine(self):
        """QAEngineのフィクスチャ"""
        with patch('src.response_engine.qa_engine.KnowledgeRetriever'), \
             patch('src.response_engine.qa_engine.LLMClient'):
            engine = QAEngine()
            yield engine
    
    def test_set_mode(self, qa_engine):
        """モード設定のテスト"""
        # 通常モード
        qa_engine.set_mode(ResponseMode.NORMAL)
        assert qa_engine.mode == ResponseMode.NORMAL
        
        # ヒントモード
        qa_engine.set_mode(ResponseMode.HINT)
        assert qa_engine.mode == ResponseMode.HINT
    
    def test_answer_normal_mode(self, qa_engine):
        """通常モードでの回答テスト"""
        qa_engine.set_mode(ResponseMode.NORMAL)
        
        # モックの設定
        qa_engine.retriever.get_context = Mock(return_value="テストコンテキスト")
        qa_engine.retriever.retrieve = Mock(return_value=[])
        qa_engine.llm_client.generate_with_context = Mock(return_value="テスト回答")
        
        # 回答の生成
        result = qa_engine.answer("テスト質問")
        
        assert result["response"] == "テスト回答"
        assert result["mode"] == "normal"
        assert result["context_used"] == True
    
    def test_conversation_history(self, qa_engine):
        """会話履歴のテスト"""
        qa_engine.llm_client.generate_with_context = Mock(return_value="回答1")
        qa_engine.retriever.get_context = Mock(return_value="")
        qa_engine.retriever.retrieve = Mock(return_value=[])
        
        # 最初の質問
        qa_engine.answer("質問1")
        assert len(qa_engine.conversation_history) == 2
        
        # 2つ目の質問
        qa_engine.answer("質問2")
        assert len(qa_engine.conversation_history) == 4
        
        # 履歴のクリア
        qa_engine.clear_history()
        assert len(qa_engine.conversation_history) == 0


class TestHintGenerator:
    """HintGeneratorのテスト"""
    
    @pytest.fixture
    def hint_generator(self):
        """HintGeneratorのフィクスチャ"""
        with patch('src.response_engine.hint_generator.LLMClient'), \
             patch('src.response_engine.hint_generator.KnowledgeRetriever'):
            generator = HintGenerator()
            yield generator
    
    def test_generate_hint_levels(self, hint_generator):
        """段階的ヒント生成のテスト"""
        hint_generator.llm_client.generate_with_context = Mock(return_value="ヒント内容")
        hint_generator.retriever.get_context = Mock(return_value="コンテキスト")
        
        # 最初のヒント（レベル1）
        result1 = hint_generator.generate_hint("テスト質問")
        assert result1["level"] == 1
        assert result1["next_level_available"] == True
        
        # 2回目のヒント（レベル2）
        result2 = hint_generator.generate_hint("テスト質問")
        assert result2["level"] == 2
        assert result2["next_level_available"] == True
        
        # 3回目のヒント（レベル3）
        result3 = hint_generator.generate_hint("テスト質問")
        assert result3["level"] == 3
        assert result3["next_level_available"] == False
    
    def test_reset_hint_level(self, hint_generator):
        """ヒントレベルのリセットテスト"""
        hint_generator.llm_client.generate_with_context = Mock(return_value="ヒント")
        hint_generator.retriever.get_context = Mock(return_value="")
        
        # ヒントを生成
        hint_generator.generate_hint("質問1")
        hint_generator.generate_hint("質問1")
        
        # 特定の質問のレベルをリセット
        hint_generator.reset_hint_level("質問1")
        
        # リセット後は再びレベル1から
        result = hint_generator.generate_hint("質問1")
        assert result["level"] == 1
    
    def test_get_hint_keywords(self, hint_generator):
        """キーワード提供のテスト"""
        from langchain.schema import Document
        
        hint_generator.retriever.retrieve = Mock(return_value=[
            Document(page_content="Pythonのリスト内包表記", metadata={})
        ])
        hint_generator.llm_client.generate_with_context = Mock(
            return_value="キーワード: リスト内包表記, Python, 内包表記"
        )
        
        result = hint_generator.get_hint_keywords("リスト内包表記について")
        assert "keywords" in result
        assert result["query"] == "リスト内包表記について"