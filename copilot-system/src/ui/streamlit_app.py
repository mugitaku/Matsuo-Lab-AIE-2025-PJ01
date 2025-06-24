import streamlit as st
import os
from pathlib import Path

from ..response_engine.qa_engine import QAEngine, ResponseMode
from ..response_engine.hint_generator import HintGenerator
from ..knowledge_base.retriever import KnowledgeRetriever


# ページ設定
st.set_page_config(
    page_title="演習サポートCopilot",
    page_icon="🤖",
    layout="wide"
)

# セッション状態の初期化
if "qa_engine" not in st.session_state:
    st.session_state.qa_engine = QAEngine()
    st.session_state.hint_generator = HintGenerator()
    st.session_state.retriever = KnowledgeRetriever()
    st.session_state.messages = []
    st.session_state.mode = ResponseMode.NORMAL

# タイトルとヘッダー
st.title("🎓 演習サポートCopilot")
st.markdown("プログラミング演習の質問にお答えします。")

# サイドバー
with st.sidebar:
    st.header("設定")
    
    # モード選択
    mode_option = st.radio(
        "応答モード",
        ["通常モード", "ヒントモード"],
        help="通常モード: 直接的な回答を提供\nヒントモード: 段階的なヒントを提供"
    )
    
    if mode_option == "ヒントモード":
        st.session_state.qa_engine.set_mode(ResponseMode.HINT)
        st.session_state.mode = ResponseMode.HINT
    else:
        st.session_state.qa_engine.set_mode(ResponseMode.NORMAL)
        st.session_state.mode = ResponseMode.NORMAL
    
    st.divider()
    
    # 演習資料のアップロード
    st.header("演習資料の管理")
    uploaded_files = st.file_uploader(
        "演習資料をアップロード",
        type=['pdf', 'txt', 'md', 'py'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        upload_dir = Path("data/exercises/uploaded")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        for uploaded_file in uploaded_files:
            file_path = upload_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ {uploaded_file.name} をアップロードしました")
        
        # インデックスの更新
        if st.button("インデックスを更新"):
            with st.spinner("インデックスを更新中..."):
                count = st.session_state.retriever.index_documents(str(upload_dir))
                st.success(f"✅ {count}個のドキュメントチャンクをインデックス化しました")
    
    st.divider()
    
    # 会話履歴のクリア
    if st.button("会話履歴をクリア"):
        st.session_state.messages = []
        st.session_state.qa_engine.clear_history()
        st.session_state.hint_generator.reset_hint_level()
        st.rerun()

# メインチャット画面
st.header("💬 チャット")

# 会話履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # ヒントレベルの表示
        if message.get("hint_level"):
            st.caption(f"ヒントレベル: {message['hint_level']}/3")

# チャット入力
if prompt := st.chat_input("演習に関する質問を入力してください..."):
    # ユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # アシスタントの応答
    with st.chat_message("assistant"):
        with st.spinner("考え中..."):
            if st.session_state.mode == ResponseMode.HINT:
                # ヒントモードの場合
                hint_response = st.session_state.hint_generator.generate_hint(prompt)
                response_text = hint_response["hint"]
                hint_level = hint_response["level"]
                
                st.markdown(response_text)
                st.caption(f"ヒントレベル: {hint_level}/3")
                
                # 次のレベルのヒントボタン
                if hint_response["next_level_available"]:
                    if st.button("もう少し詳しいヒントを見る"):
                        next_hint = st.session_state.hint_generator.generate_hint(prompt)
                        st.markdown(next_hint["hint"])
                        st.caption(f"ヒントレベル: {next_hint['level']}/3")
                
                # メッセージに追加
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "hint_level": hint_level
                })
            else:
                # 通常モードの場合
                response = st.session_state.qa_engine.answer(prompt)
                response_text = response["response"]
                
                st.markdown(response_text)
                
                # 参照した文書を表示
                if response.get("retrieved_documents"):
                    with st.expander("参照した文書"):
                        for i, doc in enumerate(response["retrieved_documents"]):
                            st.caption(f"文書 {i+1}: {doc['metadata'].get('source', 'Unknown')}")
                            st.text(doc["content"])
                
                # メッセージに追加
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })

# フッター
st.divider()
st.caption("🤖 演習サポートCopilot - AI による学習支援システム")