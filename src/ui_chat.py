import streamlit as st
import datetime
from collections import defaultdict
from src.api_gemini import get_diet_response
from src.api_gsheet import add_record

def render_bubble(msg):
    is_user = msg["role"] == "user"
    
    # Pikachu style for user
    if is_user:
        bg_color = "linear-gradient(135deg, #FFD700, #FFA500)" 
        text_color = "#111"
        box_shadow = "0 4px 15px rgba(255, 215, 0, 0.4)"
        border = "1px solid rgba(255,255,255,0.7)"
        avatar = "⚡️"
    # Tesla style for AI
    else:
        bg_color = "linear-gradient(135deg, #2b2b2b, #1a1a1a)"
        text_color = "#fff"
        box_shadow = "0 4px 15px rgba(255, 51, 102, 0.4)" 
        border = "1px solid #FF3366"
        avatar = "🍰"
        
    html = f"""
    <div style="display: flex; flex-direction: {'row-reverse' if is_user else 'row'}; align-items: flex-start; margin-bottom: 20px; font-family: 'Orbitron', sans-serif;">
        <div style="font-size: 30px; padding: 0 12px; filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));">{avatar}</div>
        <div style="background: {bg_color}; color: {text_color}; padding: 14px 20px; border-radius: 20px; max-width: 75%; word-break: break-word; box-shadow: {box_shadow}; border: {border}; line-height: 1.5; font-size: 16px; font-weight: bold; position: relative; z-index: 10;">
            {msg['content'].replace(chr(10), '<br>')}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_chat(current_weight: float):
    st.subheader("今日の記録💬 (エレクトリック・モード)")
    
    # ユーザー入力
    user_input = st.chat_input("例: 12時にお弁当食べたよ！")
    
    if user_input:
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        
        # ユーザーのメッセージを追加
        st.session_state.messages.append({"role": "user", "content": user_input, "date": today_date})
        
        # AI処理
        with st.spinner("⚡️AIテスラ思考中..."):
            response_data = get_diet_response(st.session_state.messages)
            reply_text = response_data.get("reply_message", "ごめんね、ショートしちゃった！")
            status = response_data.get("status", "error")
            
        # AIの返信を追加
        st.session_state.messages.append({"role": "assistant", "content": reply_text, "date": today_date})
        
        if status == "complete":
            ext_date = response_data.get("extracted_date", "")
            ext_time = response_data.get("extracted_time", "")
            ext_food = response_data.get("extracted_food", "")
            ext_cal = response_data.get("extracted_calories", 0)
            
            add_record(ext_date, ext_time, ext_food, ext_cal, reply_text, current_weight)
            st.toast("⚡️ スプレッドシートに記録しました！")
            
    # メッセージを日付ごとにグループ化
    chat_by_date = defaultdict(list)
    for msg in st.session_state.messages:
        d = msg.get("date", "📝 過去の記録")
        if not d: d = "📝 過去の記録"
        chat_by_date[d].append(msg)
        
    dates = sorted(list(chat_by_date.keys())) # 古い順（時系列）
    
    # スクロール可能なコンテナでやり取りを表示
    with st.container(height=600):
        for d in dates:
            st.markdown(f"<div style='text-align: center; color: #FFD700; margin: 15px 0; font-weight: bold;'>⚡️ {d} ⚡️</div>", unsafe_allow_html=True)
            for msg in chat_by_date[d]:
                render_bubble(msg)
