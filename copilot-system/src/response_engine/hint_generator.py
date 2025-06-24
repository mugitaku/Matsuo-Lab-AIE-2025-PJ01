from typing import Dict, Any, Optional
from enum import Enum

from ..llm.client import LLMClient
from ..llm.prompts import HINT_LEVEL_PROMPTS
from ..knowledge_base.retriever import KnowledgeRetriever


class HintLevel(Enum):
    """ヒントレベル"""
    BASIC = 1      # 基本的なヒント
    INTERMEDIATE = 2  # 中級ヒント
    DETAILED = 3   # 詳細なヒント


class HintGenerator:
    """段階的なヒントを生成するクラス"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.retriever = KnowledgeRetriever()
        self.hint_history: Dict[str, int] = {}  # 質問ごとのヒントレベルを記録
    
    def generate_hint(self, 
                     query: str, 
                     error_message: Optional[str] = None,
                     code_context: Optional[str] = None) -> Dict[str, Any]:
        """段階的なヒントを生成"""
        
        # 現在のヒントレベルを取得（初回は1）
        current_level = self.hint_history.get(query, 0) + 1
        current_level = min(current_level, 3)  # 最大レベルは3
        
        # ヒントレベルを更新
        self.hint_history[query] = current_level
        
        # 関連するコンテキストを取得
        context = self.retriever.get_context(query)
        
        # プロンプトの構築
        hint_prompt = self._build_hint_prompt(
            query=query,
            level=HintLevel(current_level),
            error_message=error_message,
            code_context=code_context,
            knowledge_context=context
        )
        
        # ヒントの生成
        system_prompt = """あなたは教育的なプログラミングアシスタントです。
学生が自分で問題を解決できるよう、段階的なヒントを提供してください。
直接的な答えは避け、考え方や調べ方を示してください。"""
        
        hint_response = self.llm_client.generate_with_context(
            query=hint_prompt,
            context="",
            system_prompt=system_prompt
        )
        
        return {
            "hint": hint_response,
            "level": current_level,
            "max_level": 3,
            "next_level_available": current_level < 3,
            "query": query
        }
    
    def _build_hint_prompt(self, 
                          query: str,
                          level: HintLevel,
                          error_message: Optional[str],
                          code_context: Optional[str],
                          knowledge_context: str) -> str:
        """ヒント生成用のプロンプトを構築"""
        
        prompt_parts = [
            f"学生の質問: {query}",
            f"\nヒントレベル: {level.value}/3",
            HINT_LEVEL_PROMPTS[level.value]
        ]
        
        if error_message:
            prompt_parts.append(f"\nエラーメッセージ:\n{error_message}")
            
        if code_context:
            prompt_parts.append(f"\nコードの文脈:\n{code_context}")
            
        if knowledge_context:
            prompt_parts.append(f"\n参考資料の概要:\n{knowledge_context[:500]}...")
        
        prompt_parts.append("\n上記の情報を基に、適切なレベルのヒントを提供してください。")
        
        return "\n".join(prompt_parts)
    
    def reset_hint_level(self, query: Optional[str] = None):
        """ヒントレベルをリセット"""
        if query:
            self.hint_history.pop(query, None)
        else:
            self.hint_history.clear()
    
    def get_hint_keywords(self, query: str) -> Dict[str, Any]:
        """質問に関連するキーワードやコンセプトを提供"""
        
        # 関連文書から重要なキーワードを抽出
        documents = self.retriever.retrieve(query, k=3)
        
        keyword_prompt = f"""以下の質問に関連する重要なキーワードやコンセプトを5つまで挙げてください：

質問: {query}

参考資料:
{' '.join([doc.page_content[:200] for doc in documents])}

キーワードは学生が自分で調べられるような、検索しやすい用語にしてください。
"""
        
        keywords_response = self.llm_client.generate_with_context(
            query=keyword_prompt,
            context="",
            system_prompt="プログラミング教育の専門家として、学習に役立つキーワードを提供してください。"
        )
        
        return {
            "keywords": keywords_response,
            "query": query
        }