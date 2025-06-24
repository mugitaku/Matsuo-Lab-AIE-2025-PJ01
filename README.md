# 演習をサポートするCopilotの作成

プロジェクトの詳細は、所定のドキュメントを確認すること。

## 実装について

### 演習サポートCopilotの実装計画

プロジェクト構造

copilot-system/
├── src/
│   ├── __init__.py
│   ├── main.py                 # メインエントリーポイント
│   ├── knowledge_base/         # 演習資料管理
│   │   ├── __init__.py
│   │   ├── document_loader.py  # 資料読み込み
│   │   ├── vector_store.py     # ベクトルDB管理
│   │   └── retriever.py        # 検索機能
│   ├── llm/                    # LLM連携
│   │   ├── __init__.py
│   │   ├── client.py           # LLMクライアント
│   │   └── prompts.py          # プロンプトテンプレート
│   ├── response_engine/        # 応答エンジン
│   │   ├── __init__.py
│   │   ├── qa_engine.py        # 質問応答
│   │   └── hint_generator.py   # ヒント生成
│   ├── ui/                     # UIコンポーネント
│   │   ├── __init__.py
│   │   └── streamlit_app.py    # Streamlit UI
│   └── utils/                  # ユーティリティ
│       ├── __init__.py
│       ├── config.py           # 設定管理
│       └── evaluator.py        # 回答評価
├── data/
│   └── exercises/              # 演習資料格納
├── tests/                      # テストコード
├── requirements.txt
├── .env.example
└── README.md

技術スタック

1. Python 3.9+
2. LangChain - RAGシステム構築
3. ChromaDB/FAISS - ベクトルデータベース
4. OpenAI API/Claude API - LLM
5. Streamlit - Web UI
6. pytest - テスト

実装フェーズ

フェーズ1: 基盤構築
- プロジェクト構造のセットアップ
- 設定管理システムの実装
- 基本的なLLMクライアントの実装

フェーズ2: RAGシステム
- 演習資料のローダー実装
- ベクトルストアへのインデックス作成
- 類似文書検索機能

フェーズ3: 応答エンジン
- 質問応答の基本実装
- ヒント生成ロジック（直接回答を避ける）
- コンテキスト管理

フェーズ4: UI開発
- Streamlitでのチャット画面実装
- モード切替機能（通常/ヒントモード）
- 演習資料アップロード機能

フェーズ5: 拡張機能
- 回答品質評価システム
- ログ収集と分析
- パフォーマンス最適化

主要機能の実装方針

1. RAGシステム
- LangChainのDocument LoaderでPDF/テキストファイルを読み込み
- テキストを適切なチャンクに分割
- ChromaDBでベクトル化して保存
2. ヒント生成
- プロンプトエンジニアリングで直接回答を避ける
- 段階的なヒント提供（レベル1〜3）
- 学習者の理解度に応じた調整
3. 評価システム
- 回答の関連性スコア
- ヒントの適切性評価
- 学習効果の測定指標

### 設計方針

本システムは以下の設計方針に基づいて実装されています：

1. **モジュラー設計**
   - 各機能を独立したモジュールとして実装し、保守性と拡張性を確保
   - knowledge_base（RAG）、llm（LLM連携）、response_engine（応答生成）、ui（インターフェース）に分離

2. **RAGアーキテクチャの採用**
   - 演習資料を効率的に検索・参照するためLangChainとベクトルデータベースを使用
   - ChromaDBとFAISSの両方に対応し、用途に応じて選択可能

3. **教育的配慮**
   - 通常モードとヒントモードを明確に分離
   - ヒントモードでは3段階の段階的なヒントを提供し、学習者の思考を促進

4. **ユーザビリティ重視**
   - Streamlitによる直感的なWeb UI
   - ドラッグ&ドロップでの資料追加機能
   - 会話履歴の保持と参照

5. **拡張性の確保**
   - 新しいLLMモデルへの対応が容易
   - 評価システムによる継続的な品質改善
   - プラグイン形式での機能追加が可能

### システムの使用方法

#### 1. セットアップ

```bash
cd PJT01_発注書_演習をサポートするCopilotの作成

# 環境設定ファイルの準備
cp copilot-system/.env.example copilot-system/.env

# .envファイルを編集してOpenAI APIキーを設定
# OPENAI_API_KEY=your_openai_api_key_here

# 依存パッケージのインストール
cd copilot-system
pip install -r requirements.txt
```

#### 2. システムの起動

```bash
# copilot-systemディレクトリで実行
python src/main.py
```

起動すると自動的にブラウザが開き、Streamlit UIが表示されます。

#### 3. 演習資料の追加

1. サイドバーの「演習資料の管理」セクションを開く
2. PDF、TXT、MD、PYファイルをドラッグ&ドロップまたは選択
3. 「インデックスを更新」ボタンをクリック

#### 4. 質問応答の利用

**通常モード（デフォルト）**
- 演習内容に関する質問に対して直接的な回答を提供
- コードの実装例や詳細な説明を含む

**ヒントモード**
- サイドバーで「ヒントモード」を選択
- 段階的なヒントを提供（レベル1〜3）
- 「もう少し詳しいヒントを見る」ボタンで次のレベルへ

#### 5. 高度な機能

**回答品質の評価**
```python
from src.utils.evaluator import ResponseEvaluator

evaluator = ResponseEvaluator()
# 回答の自動評価と改善提案の生成
```

**プログラムからの利用**
```python
from src.response_engine.qa_engine import QAEngine, ResponseMode

# エンジンの初期化
qa_engine = QAEngine()

# 通常モードで回答
qa_engine.set_mode(ResponseMode.NORMAL)
result = qa_engine.answer("リスト内包表記の使い方を教えてください")

# ヒントモードで回答
qa_engine.set_mode(ResponseMode.HINT)
hint_result = qa_engine.answer("デコレータの実装方法がわかりません")
```

### トラブルシューティング

- **APIキーエラー**: .envファイルにOpenAI APIキーが正しく設定されているか確認
- **インデックスエラー**: data/exercises/ディレクトリに演習資料が存在するか確認
- **ポートエラー**: デフォルトポート8501が使用中の場合は.envでAPP_PORTを変更

### 開発者向け情報

詳細な実装内容とAPIドキュメントは `copilot-system/README.md` を参照してください。
