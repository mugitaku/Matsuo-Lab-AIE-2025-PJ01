import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.knowledge_base.retriever import KnowledgeRetriever
from src.utils.config import settings


def initialize_system():
    """システムの初期化"""
    print("🚀 演習サポートCopilotを初期化しています...")
    
    # 必要なディレクトリの作成
    Path(settings.exercises_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.vector_store_path).mkdir(parents=True, exist_ok=True)
    
    # 知識ベースの初期化
    retriever = KnowledgeRetriever()
    
    # 演習資料のインデックス化
    if os.listdir(settings.exercises_dir):
        print(f"📚 {settings.exercises_dir} から演習資料を読み込んでいます...")
        count = retriever.index_documents()
        print(f"✅ {count}個のドキュメントチャンクをインデックス化しました")
    else:
        print("⚠️  演習資料が見つかりません。data/exercises/ に資料を配置してください")
    
    return retriever


def run_streamlit():
    """Streamlitアプリの起動"""
    import subprocess
    
    print("\n🌐 Webインターフェースを起動しています...")
    app_path = Path(__file__).parent / "ui" / "streamlit_app.py"
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", str(settings.app_port),
        "--server.headless", "true"
    ])


def main():
    """メインエントリーポイント"""
    print("=" * 50)
    print("🎓 演習サポートCopilot")
    print("=" * 50)
    
    # APIキーのチェック
    if not settings.openai_api_key:
        print("❌ エラー: OPENAI_API_KEY が設定されていません")
        print("💡 .env ファイルを作成し、APIキーを設定してください")
        print("   cp .env.example .env")
        print("   その後、.env ファイルを編集してAPIキーを入力してください")
        return
    
    # システムの初期化
    try:
        initialize_system()
    except Exception as e:
        print(f"❌ 初期化エラー: {str(e)}")
        return
    
    # Streamlitアプリの起動
    try:
        run_streamlit()
    except KeyboardInterrupt:
        print("\n👋 アプリケーションを終了します")
    except Exception as e:
        print(f"❌ エラー: {str(e)}")


if __name__ == "__main__":
    main()