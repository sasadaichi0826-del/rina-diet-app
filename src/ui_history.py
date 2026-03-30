import streamlit as st
import pandas as pd
import plotly.express as px
import re
from src.api_gsheet import get_weight_data, update_all_records

def render_history_and_graph():
    records = get_weight_data()
    
    if not records:
        st.info("まだ記録がありません。スプレッドシートへのテスト書き込みを行うか、チャットを送信してください。")
        return
        
    df = pd.DataFrame(records)
    
    # グラフセクション (カロリー摂取量推移)
    st.subheader("摂取カロリーの推移🔥 (目標: 1400kcal)")
    
    if '日付' in df.columns and 'カロリー' in df.columns:
        df_graph = df.copy()
        df_graph['カロリー'] = pd.to_numeric(df_graph['カロリー'], errors='coerce').fillna(0)
        df_daily = df_graph.groupby('日付')['カロリー'].sum().reset_index()
        
        if not df_daily.empty:
            fig = px.bar(df_daily, x='日付', y='カロリー', title='毎日の摂取カロリー')
            fig.add_hline(y=1400, line_dash="dash", line_color="#FF3366", annotation_text="目標 (1400kcal)")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Mochiy Pop P One"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("カロリーの記録がまだありません。")
            
    st.markdown("---")
    
    # 双方向編集データテーブルセクション
    st.subheader("✏️ データ編集 (スプレッドシート直結)")
    st.write("ここで表のデータを直接書き換えて「保存」ボタンを押すと、スプレッドシートに反映されます！")
    
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 スプレッドシートに保存"):
        with st.spinner("スプレッドシートを更新中...⚡️"):
            clean_df = edited_df.fillna("")
            if update_all_records(clean_df):
                st.success("✅ スプレッドシートを更新しました！リロードして確認してください。")
            else:
                st.error("❌ 更新に失敗しました。")
                
    st.markdown("---")
    
    # タイムライン (カード型UI) セクション
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("最近の記録📋")
    with col2:
        sort_order = st.radio("記録の並び順", ["新しい順", "古い順"], horizontal=True, key="history_sort")
        
    # 日付ごとにグループ化
    history_by_date = {}
    for record in records:
        date = record.get('日付', '')
        legacy_log = record.get('入力ログ', '')
        food_content = record.get('内容', '')
        if not date and not legacy_log and not food_content:
            continue
        if not date: date = "📝 過去の記録"
        if date not in history_by_date:
            history_by_date[date] = []
        history_by_date[date].append(record)
        
    is_newest_first = (sort_order == "新しい順")
    dates = sorted(list(history_by_date.keys()), reverse=is_newest_first)
    
    for i, d in enumerate(dates):
        day_records = history_by_date[d]
        
        # カロリー計算
        total_cal = 0
        for r in day_records:
            cal = r.get("カロリー", "")
            if str(cal).isdigit():
                total_cal += int(cal)
            elif not cal: # 旧形式の場合
                log = r.get("入力ログ", "")
                match = re.search(r'【推定カロリー】\s*(\d+)', log)
                if match:
                    total_cal += int(match.group(1))
                
        # アコーディオン（先頭の1つだけ開く）
        with st.expander(f"📅 {d} (合計: {total_cal} kcal)", expanded=(i == 0)):
            # "新しい順"ならその日の記録も最新を上に
            display_records = reversed(day_records) if is_newest_first else day_records
            
            for record in display_records:
                with st.container(border=True):
                    # 旧形式と新形式の対応
                    legacy_log = record.get("入力ログ", "")
                    if legacy_log:
                        st.info(legacy_log)
                    else:
                        time_str = record.get("時間", "")
                        food_str = record.get("内容", "未入力")
                        cal_str = record.get("カロリー", "0")
                        
                        display_text = ""
                        if time_str: display_text += f"⏰ {time_str}　"
                        if food_str: display_text += f"🍽️ {food_str}　"
                        if cal_str and str(cal_str) != "0": display_text += f"🔥 {cal_str} kcal"
                        
                        if display_text.strip():
                            st.info(display_text)
                    
                    ai_reply = record.get('AI返信', '')
                    if ai_reply:
                        st.success(f"**AIからのアドバイス🍰**\n\n{ai_reply}")
