from typing import List, Optional
import os
from pathlib import Path

from langchain.vectorstores import Chroma, FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

from ..utils.config import settings


class VectorStore:
    """ベクトルストアを管理するクラス"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key
        )
        self.vector_store = None
        self._initialize_store()
    
    def _initialize_store(self):
        """ベクトルストアを初期化"""
        Path(settings.vector_store_path).mkdir(parents=True, exist_ok=True)
        
        if settings.vector_store_type == "chroma":
            self.vector_store = Chroma(
                persist_directory=settings.vector_store_path,
                embedding_function=self.embeddings
            )
        elif settings.vector_store_type == "faiss":
            # FAISSの場合、既存のインデックスがあれば読み込む
            index_path = os.path.join(settings.vector_store_path, "faiss_index")
            if os.path.exists(index_path):
                self.vector_store = FAISS.load_local(
                    index_path, 
                    self.embeddings
                )
            else:
                # 新規作成（ダミー文書で初期化）
                dummy_doc = [Document(page_content="init", metadata={"type": "init"})]
                self.vector_store = FAISS.from_documents(
                    dummy_doc, 
                    self.embeddings
                )
    
    def add_documents(self, documents: List[Document]) -> None:
        """文書をベクトルストアに追加"""
        if not documents:
            return
            
        if self.vector_store is None:
            self._initialize_store()
            
        self.vector_store.add_documents(documents)
        
        # 永続化
        if settings.vector_store_type == "chroma":
            self.vector_store.persist()
        elif settings.vector_store_type == "faiss":
            index_path = os.path.join(settings.vector_store_path, "faiss_index")
            self.vector_store.save_local(index_path)
    
    def search(self, query: str, k: int = 5, filter: Optional[dict] = None) -> List[Document]:
        """類似文書を検索"""
        if self.vector_store is None:
            return []
            
        if filter:
            return self.vector_store.similarity_search(
                query, 
                k=k, 
                filter=filter
            )
        else:
            return self.vector_store.similarity_search(query, k=k)
    
    def search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """スコア付きで類似文書を検索"""
        if self.vector_store is None:
            return []
            
        return self.vector_store.similarity_search_with_score(query, k=k)
    
    def delete_all(self) -> None:
        """全ての文書を削除"""
        if settings.vector_store_type == "chroma":
            self.vector_store.delete_collection()
        elif settings.vector_store_type == "faiss":
            # FAISSの場合は再初期化
            dummy_doc = [Document(page_content="init", metadata={"type": "init"})]
            self.vector_store = FAISS.from_documents(
                dummy_doc, 
                self.embeddings
            )