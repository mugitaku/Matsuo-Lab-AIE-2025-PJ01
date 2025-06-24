from typing import Optional, List, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage

from ..utils.config import settings


class LLMClient:
    """LLMクライアントクラス"""
    
    def __init__(self, streaming: bool = False):
        self.streaming = streaming
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else []
        
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model_name=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            streaming=streaming,
            callbacks=callbacks
        )
    
    def generate(self, messages: List[BaseMessage]) -> str:
        """メッセージリストから応答を生成"""
        response = self.llm(messages)
        return response.content
    
    def generate_with_context(self, 
                            query: str, 
                            context: str, 
                            system_prompt: Optional[str] = None) -> str:
        """コンテキスト付きで応答を生成"""
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        # コンテキストを含むユーザーメッセージ
        if context:
            user_message = f"以下の参考資料を基に質問に答えてください。\n\n参考資料:\n{context}\n\n質問: {query}"
        else:
            user_message = query
            
        messages.append(HumanMessage(content=user_message))
        
        return self.generate(messages)
    
    def create_chat_history(self, history: List[Dict[str, str]]) -> List[BaseMessage]:
        """会話履歴からメッセージリストを作成"""
        messages = []
        
        for item in history:
            role = item.get("role", "")
            content = item.get("content", "")
            
            if role == "system":
                messages.append(SystemMessage(content=content))
            elif role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
                
        return messages
    
    def count_tokens(self, text: str) -> int:
        """テキストのトークン数をカウント"""
        return self.llm.get_num_tokens(text)