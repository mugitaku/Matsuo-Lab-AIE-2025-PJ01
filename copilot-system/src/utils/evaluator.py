from typing import Dict, Any, List
import json

from ..llm.client import LLMClient
from ..llm.prompts import EVALUATION_PROMPT


class ResponseEvaluator:
    """回答品質を評価するクラス"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.evaluation_history: List[Dict[str, Any]] = []
    
    def evaluate_response(self, 
                         query: str, 
                         response: str, 
                         mode: str,
                         context: str = "") -> Dict[str, Any]:
        """回答の品質を評価"""
        
        evaluation_prompt = f"""以下の質問と回答を評価してください。

質問: {query}

回答: {response}

モード: {mode}

参考にした文脈:
{context[:500] if context else "なし"}

{EVALUATION_PROMPT}
"""
        
        # 評価の実行
        evaluation_result = self.llm_client.generate_with_context(
            query=evaluation_prompt,
            context="",
            system_prompt="教育専門家として、回答の品質を客観的に評価してください。"
        )
        
        # 評価結果の解析
        scores = self._parse_evaluation(evaluation_result)
        
        # 評価履歴に追加
        evaluation_record = {
            "query": query,
            "response": response[:200] + "...",
            "mode": mode,
            "scores": scores,
            "total_score": sum(scores.values()),
            "evaluation": evaluation_result
        }
        self.evaluation_history.append(evaluation_record)
        
        return evaluation_record
    
    def _parse_evaluation(self, evaluation_text: str) -> Dict[str, int]:
        """評価テキストからスコアを抽出"""
        scores = {
            "accuracy": 0,
            "clarity": 0,
            "relevance": 0,
            "educational_value": 0,
            "hint_appropriateness": 0
        }
        
        # 簡易的なパース（実際はより洗練された方法を使用）
        lines = evaluation_text.split('\n')
        for line in lines:
            for key in scores:
                if key.replace('_', ' ').lower() in line.lower():
                    # 数字を探す
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        scores[key] = int(numbers[0])
                        break
        
        return scores
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """評価履歴のサマリーを取得"""
        if not self.evaluation_history:
            return {
                "total_evaluations": 0,
                "average_scores": {},
                "mode_breakdown": {}
            }
        
        # 平均スコアの計算
        total_scores = {
            "accuracy": 0,
            "clarity": 0,
            "relevance": 0,
            "educational_value": 0,
            "hint_appropriateness": 0
        }
        
        mode_counts = {"normal": 0, "hint": 0}
        mode_scores = {"normal": 0, "hint": 0}
        
        for record in self.evaluation_history:
            for key, value in record["scores"].items():
                total_scores[key] += value
            
            mode = record["mode"]
            if mode in mode_counts:
                mode_counts[mode] += 1
                mode_scores[mode] += record["total_score"]
        
        # 平均の計算
        num_evaluations = len(self.evaluation_history)
        average_scores = {
            key: value / num_evaluations 
            for key, value in total_scores.items()
        }
        
        # モード別平均
        mode_averages = {}
        for mode in mode_counts:
            if mode_counts[mode] > 0:
                mode_averages[mode] = mode_scores[mode] / mode_counts[mode]
        
        return {
            "total_evaluations": num_evaluations,
            "average_scores": average_scores,
            "total_average": sum(average_scores.values()),
            "mode_breakdown": {
                "counts": mode_counts,
                "average_scores": mode_averages
            }
        }
    
    def export_evaluation_report(self, filepath: str):
        """評価レポートをエクスポート"""
        summary = self.get_evaluation_summary()
        
        report = {
            "summary": summary,
            "detailed_evaluations": self.evaluation_history
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def suggest_improvements(self, evaluation_record: Dict[str, Any]) -> str:
        """評価結果に基づいて改善提案を生成"""
        scores = evaluation_record["scores"]
        
        improvement_prompt = f"""以下の評価結果に基づいて、回答品質を改善するための具体的な提案を3つ提供してください：

評価スコア:
- 正確性: {scores['accuracy']}/10
- 明確性: {scores['clarity']}/10
- 関連性: {scores['relevance']}/10
- 教育的価値: {scores['educational_value']}/10
- ヒントの適切性: {scores['hint_appropriateness']}/10

特に低いスコアの項目に焦点を当てて、実行可能な改善策を提案してください。
"""
        
        improvements = self.llm_client.generate_with_context(
            query=improvement_prompt,
            context="",
            system_prompt="教育コンテンツの専門家として、具体的で実行可能な改善提案を提供してください。"
        )
        
        return improvements