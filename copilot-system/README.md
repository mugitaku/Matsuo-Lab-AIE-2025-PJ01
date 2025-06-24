# 演習サポートCopilot

松尾研のAI講義における演習をサポートするAIチャットボットシステムです。

## 機能

- **演習資料に基づいた質問対応**: RAGシステムを使用して演習資料から関連情報を検索し、的確な回答を提供
- **ヒント提供モード**: 直接的な答えではなく、段階的なヒントを提供して学習を促進
- **自然言語での対話**: 日本語での自然な質問応答に対応
- **動的な資料追加**: Web UIから新しい演習資料を簡単に追加可能
- **回答品質評価**: 回答の品質を自動評価し、改善提案を生成（発展的機能）

## インストール

### 1. リポジトリのクローン
```bash
git clone <repository_url>
cd copilot-system
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. 環境設定
```bash
cp .env.example .env
```

`.env`ファイルを編集して、OpenAI APIキーを設定してください：
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 使用方法

### 1. アプリケーションの起動
```bash
python src/main.py
```

ブラウザが自動的に開き、Streamlit UIが表示されます。

### 2. 演習資料の追加
- サイドバーの「演習資料の管理」セクションからファイルをアップロード
- 対応形式: PDF, TXT, MD, PY
- 「インデックスを更新」をクリックして資料を検索可能にする

### 3. 質問応答
- チャット画面で質問を入力
- 通常モード：直接的な回答を提供
- ヒントモード：段階的なヒントを提供

## プロジェクト構造

```
copilot-system/
├── src/
│   ├── knowledge_base/     # RAGシステム
│   ├── llm/               # LLM連携
│   ├── response_engine/   # 応答エンジン
│   ├── ui/               # Web UI
│   └── utils/            # ユーティリティ
├── data/
│   └── exercises/        # 演習資料
├── tests/               # テストコード
└── requirements.txt
```

## 開発

### テストの実行
```bash
pytest tests/
```

### カスタマイズ

#### LLMモデルの変更
`.env`ファイルの`MODEL_NAME`を変更：
```
MODEL_NAME=gpt-4
```

#### ベクトルストアの変更
`.env`ファイルの`VECTOR_STORE_TYPE`を変更：
```
VECTOR_STORE_TYPE=faiss  # または chroma
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。