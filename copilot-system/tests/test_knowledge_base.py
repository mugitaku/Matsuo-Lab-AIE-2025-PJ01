import pytest
import tempfile
import os
from pathlib import Path

from src.knowledge_base.document_loader import DocumentLoader
from src.knowledge_base.vector_store import VectorStore
from src.knowledge_base.retriever import KnowledgeRetriever


class TestDocumentLoader:
    """DocumentLoaderのテスト"""
    
    def test_load_text_file(self):
        """テキストファイルの読み込みテスト"""
        loader = DocumentLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("これはテストファイルです。\nPythonプログラミングについて学習します。")
            temp_path = f.name
        
        try:
            documents = loader._load_text(temp_path)
            assert len(documents) > 0
            assert "テストファイル" in documents[0].page_content
        finally:
            os.unlink(temp_path)
    
    def test_text_splitting(self):
        """テキスト分割のテスト"""
        loader = DocumentLoader()
        
        # 長いテキストを作成
        long_text = "。".join([f"これは{i}番目の文です" for i in range(100)])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(long_text)
            temp_path = f.name
        
        try:
            documents = loader._load_text(temp_path)
            # 複数のチャンクに分割されることを確認
            assert len(documents) > 1
        finally:
            os.unlink(temp_path)
    
    def test_load_directory(self):
        """ディレクトリからの読み込みテスト"""
        loader = DocumentLoader()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # テストファイルを作成
            for i in range(3):
                file_path = Path(temp_dir) / f"test_{i}.txt"
                file_path.write_text(f"テストファイル{i}の内容")
            
            documents = loader.load_documents(temp_dir)
            assert len(documents) >= 3


class TestVectorStore:
    """VectorStoreのテスト"""
    
    @pytest.fixture
    def vector_store(self):
        """VectorStoreのフィクスチャ"""
        # テスト用の一時ディレクトリを使用
        with tempfile.TemporaryDirectory() as temp_dir:
            import src.utils.config as config
            original_path = config.settings.vector_store_path
            config.settings.vector_store_path = temp_dir
            
            store = VectorStore()
            yield store
            
            config.settings.vector_store_path = original_path
    
    def test_add_and_search_documents(self, vector_store):
        """文書の追加と検索のテスト"""
        from langchain.schema import Document
        
        # テスト文書の作成
        test_docs = [
            Document(page_content="Pythonは人気のプログラミング言語です", metadata={"source": "test1.txt"}),
            Document(page_content="機械学習にはPythonがよく使われます", metadata={"source": "test2.txt"}),
            Document(page_content="JavaScriptはWeb開発で使われます", metadata={"source": "test3.txt"})
        ]
        
        # 文書の追加
        vector_store.add_documents(test_docs)
        
        # 検索テスト
        results = vector_store.search("Python", k=2)
        assert len(results) == 2
        assert any("Python" in doc.page_content for doc in results)


class TestKnowledgeRetriever:
    """KnowledgeRetrieverのテスト"""
    
    @pytest.fixture
    def retriever(self):
        """KnowledgeRetrieverのフィクスチャ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import src.utils.config as config
            original_path = config.settings.vector_store_path
            config.settings.vector_store_path = temp_dir
            
            retriever = KnowledgeRetriever()
            yield retriever
            
            config.settings.vector_store_path = original_path
    
    def test_get_context(self, retriever):
        """コンテキスト生成のテスト"""
        from langchain.schema import Document
        
        # テスト文書を追加
        test_doc = Document(
            page_content="Pythonでリスト内包表記を使うと簡潔にコードが書けます",
            metadata={"source": "python_tips.txt"}
        )
        retriever.vector_store.add_documents([test_doc])
        
        # コンテキストの取得
        context = retriever.get_context("リスト内包表記", k=1)
        assert "リスト内包表記" in context
        assert "python_tips.txt" in context