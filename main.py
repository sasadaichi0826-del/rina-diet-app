import streamlit as st
from dotenv import load_dotenv

st.set_page_config(
    page_title="里奈ちゃんの小悪魔ダイエット",
    page_icon="🍰",  # ハト禁止
    layout="centered"
)

# .envファイルの中身の変更を強制的に上書きして反映させる
load_dotenv(override=True)
try:
    from src.api_gemini import init_gemini
    init_gemini()
except Exception as e:
    st.error(f"⚠️ Gemini API初期化エラー: {e}")

from src.state import init_session_state, sync_messages_from_sheet
from src.theme import load_css
from src.ui_chat import render_chat
from src.ui_history import render_history_and_graph

init_session_state()

st.sidebar.title("設定⚙️")
today_weight = st.sidebar.number_input("今日の体重 (kg)", min_value=40.0, max_value=100.0, value=55.0, step=0.1)

st.sidebar.markdown("---")
theme_selection = st.sidebar.radio("テーマを選択", ["エレクトリック・テスラ⚡️ (ピカチュウ×モダン)", "小悪魔 (黒×紫)", "リラックス (茶×黄)"])
st.session_state.theme = "tesla" # 強制的に新テーマを適用

st.sidebar.markdown("---")
st.sidebar.subheader("🎨 カスタムカラー設定")
bg_color = st.sidebar.color_picker("背景色", "#0a0a1a")
text_color = st.sidebar.color_picker("文字色", "#FFD700")

load_css(st.session_state.theme, bg_color=bg_color, text_color=text_color)

# ==========================================
# データ同期・デバッグ用ツール
# ==========================================
if st.sidebar.button("🔄 最新データを取得", help="スプレッドシートの最新状態と手動で同期します"):
    sync_messages_from_sheet()
    st.sidebar.success("データを同期しました！")

if st.sidebar.button("🔧 スプレッドシート接続テスト", help="エラー原因を特定するための確認ツールです"):
    from src.api_gsheet import run_connection_test
    run_connection_test()

st.title("里奈ちゃんのダイエット管理🍰⚡️")
st.write("毎日頑張ってえらい！今の体重を設定してから、食べたものや活動ログをチャットで送ってね！")

# タブ機能で画面を切り替え
tab1, tab2, tab3 = st.tabs(["チャット💬", "記録＆グラフ📈", "使い方📖"])

with tab1:
    render_chat(today_weight)

with tab2:
    render_history_and_graph()

with tab3:
    st.markdown("""
    ## 使い方📖 (エレクトリック・ダイエット・マニュアル⚡️)
    
    天才発明家ニコラ・テスラとピカチュウの電撃パワーを宿した、最新鋭のモダン3Dダイエットアプリへようこそ！
    
    ### 🔋 基本的な使い方
    1. **今の体重をセット**: 画面左側の「設定⚙️」から今日の体重を入力します。
    2. **チャットで報告💬**: チャット画面一番下の入力欄から、「12時にお弁当食べた！」「30分歩いたよ」など、AIに今日の報告を送信します。
    3. **AIがカロリーを自動計算**: 天才AIが文章からカロリーを推定し、あなたを全力で褒めながらスプレッドシートに自動記録します！
    
    ### ⚡️ 記録の確認と機能
    - **チャットタブ**: LINEのように上下にスクロールでき、過去のやり取りもすべて確認できます。「最新データを取得」ボタンで手動同期も可能です。
    - **記録＆グラフタブ**: スプレッドシートに蓄積された体重グラフと、日付ごとに折りたたまれた（アコーディオン）タイムライン履歴を確認できます。
    
    ### 🎨 テーマについて
    現在のUIは「エレクトリック・テスラ⚡️」という、ネオモーフィズム立体感＋ダークモダン＋ピカチュウのネオンカラーを合わせた最強デザインです。ボタンには電気が通っているので、押すとプルプル動きます⚡️
    """)
