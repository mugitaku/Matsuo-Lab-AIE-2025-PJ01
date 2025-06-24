from typing import List, Optional, Dict, Any
from langchain.schema import Document

from .document_loader import DocumentLoader
from .vector_store import VectorStore


class KnowledgeRetriever:
    """知識ベースから情報を検索するクラス"""
    
    def __init__(self):
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore()
        
    def index_documents(self, directory: Optional[str] = None) -> int:
        """ディレクトリ内の文書をインデックス化"""
        documents = self.document_loader.load_documents(directory)
        
        if documents:
            self.vector_store.add_documents(documents)
            print(f"Indexed {len(documents)} document chunks")
            return len(documents)
        return 0
    
    def retrieve(self, query: str, k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """クエリに関連する文書を取得"""
        return self.vector_store.search(query, k=k, filter=filter)
    
    def retrieve_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """スコア付きで関連文書を取得"""
        return self.vector_store.search_with_score(query, k=k)
    
    def get_context(self, query: str, k: int = 5) -> str:
        """クエリに関連するコンテキストを生成"""
        documents = self.retrieve(query, k=k)
        
        if not documents:
            return ""
        
        # 文書を結合してコンテキストを作成
        context_parts = []
        for i, doc in enumerate(documents):
            source = doc.metadata.get('source', 'Unknown')
            content = doc.page_content.strip()
            context_parts.append(f"[文書{i+1} - {source}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def add_single_document(self, content: str, metadata: Dict[str, Any]) -> None:
        """単一の文書を追加"""
        doc = Document(page_content=content, metadata=metadata)
        split_docs = self.document_loader.text_splitter.split_documents([doc])
        self.vector_store.add_documents(split_docs)
    
    def clear_index(self) -> None:
        """インデックスをクリア"""
        self.vector_store.delete_all()
        print("Index cleared")