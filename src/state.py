import streamlit as st
from src.api_gsheet import get_weight_data

def sync_messages_from_sheet():
    """スプレッドシートからデータを読み込み、チャット履歴に反映する"""
    records = get_weight_data()
    messages = []
    for row in records:
        date_str = row.get("日付", "")
        # 旧形式のサポート（B列が入力ログだった場合）
        legacy_log = row.get("入力ログ", "")
        
        time_str = row.get("時間", "")
        food_str = row.get("内容", "")
        cal_str = row.get("カロリー", "")
        
        ai_reply = row.get("AI返信", "")
        
        if legacy_log:
            user_log = legacy_log
        else:
            user_log = ""
            if time_str: user_log += f"【時間】{time_str}\n"
            if food_str: user_log += f"【内容】{food_str}\n"
            if cal_str and str(cal_str) != "0": user_log += f"【推定カロリー】{cal_str} kcal"
            user_log = user_log.strip()
            
        if user_log:
            messages.append({"role": "user", "content": user_log, "date": date_str})
        if ai_reply:
            messages.append({"role": "assistant", "content": ai_reply, "date": date_str})
    st.session_state.messages = messages

def init_session_state():
    """Streamlitのセッション間で保持する変数を初期化する"""
    if "messages" not in st.session_state:
        sync_messages_from_sheet()
    if "theme" not in st.session_state:
        st.session_state.theme = "devil" # 初期テーマは小悪魔
