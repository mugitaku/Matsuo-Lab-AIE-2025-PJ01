import os
from typing import List, Dict, Any
from pathlib import Path

from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from ..utils.config import settings


class DocumentLoader:
    """演習資料を読み込み、処理するクラス"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "、", " ", ""]
        )
        
    def load_documents(self, directory: str = None) -> List[Document]:
        """指定ディレクトリから全ての文書を読み込む"""
        if directory is None:
            directory = settings.exercises_dir
            
        documents = []
        
        # ディレクトリが存在しない場合は作成
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # サポートするファイル拡張子
        supported_extensions = {
            '.pdf': self._load_pdf,
            '.txt': self._load_text,
            '.md': self._load_text,
            '.py': self._load_text
        }
        
        # ディレクトリ内のファイルを走査
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path)
                
                if ext.lower() in supported_extensions:
                    loader_func = supported_extensions[ext.lower()]
                    try:
                        docs = loader_func(file_path)
                        documents.extend(docs)
                        print(f"Loaded: {file_path}")
                    except Exception as e:
                        print(f"Error loading {file_path}: {str(e)}")
                        
        return documents
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """PDFファイルを読み込む"""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def _load_text(self, file_path: str) -> List[Document]:
        """テキストファイルを読み込む"""
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def add_metadata(self, documents: List[Document], metadata: Dict[str, Any]) -> List[Document]:
        """文書にメタデータを追加"""
        for doc in documents:
            doc.metadata.update(metadata)
        return documents