from typing import Optional, Dict, Any, List
from enum import Enum

from ..knowledge_base.retriever import KnowledgeRetriever
from ..llm.client import LLMClient
from ..llm.prompts import SYSTEM_PROMPT_NORMAL, SYSTEM_PROMPT_HINT


class ResponseMode(Enum):
    """応答モード"""
    NORMAL = "normal"
    HINT = "hint"


class QAEngine:
    """質問応答エンジン"""
    
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.llm_client = LLMClient()
        self.mode = ResponseMode.NORMAL
        self.conversation_history: List[Dict[str, str]] = []
    
    def set_mode(self, mode: ResponseMode):
        """応答モードを設定"""
        self.mode = mode
    
    def answer(self, query: str, use_context: bool = True) -> Dict[str, Any]:
        """質問に回答"""
        # コンテキストの取得
        context = ""
        retrieved_docs = []
        
        if use_context:
            context = self.retriever.get_context(query)
            retrieved_docs = self.retriever.retrieve(query, k=3)
        
        # システムプロンプトの選択
        system_prompt = (
            SYSTEM_PROMPT_HINT if self.mode == ResponseMode.HINT 
            else SYSTEM_PROMPT_NORMAL
        )
        
        # 回答の生成
        response = self.llm_client.generate_with_context(
            query=query,
            context=context,
            system_prompt=system_prompt
        )
        
        # 会話履歴に追加
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return {
            "response": response,
            "mode": self.mode.value,
            "context_used": use_context,
            "retrieved_documents": [
                {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                } for doc in retrieved_docs
            ]
        }
    
    def answer_with_history(self, query: str) -> Dict[str, Any]:
        """会話履歴を考慮して回答"""
        # コンテキストの取得
        context = self.retriever.get_context(query)
        
        # システムプロンプトを含む会話履歴の作成
        system_prompt = (
            SYSTEM_PROMPT_HINT if self.mode == ResponseMode.HINT 
            else SYSTEM_PROMPT_NORMAL
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 過去の会話履歴を追加（最新の5つまで）
        recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        messages.extend(recent_history)
        
        # 現在の質問とコンテキストを追加
        if context:
            user_message = f"参考資料:\n{context}\n\n質問: {query}"
        else:
            user_message = query
            
        messages.append({"role": "user", "content": user_message})
        
        # メッセージリストの作成と回答生成
        message_objects = self.llm_client.create_chat_history(messages)
        response = self.llm_client.generate(message_objects)
        
        # 会話履歴に追加
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return {
            "response": response,
            "mode": self.mode.value,
            "context_used": bool(context),
            "history_length": len(self.conversation_history)
        }
    
    def clear_history(self):
        """会話履歴をクリア"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """会話履歴を取得"""
        return self.conversation_history