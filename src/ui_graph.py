import streamlit as st
import pandas as pd
import plotly.express as px
from src.api_gsheet import get_weight_data

def render_graph():
    st.subheader("目標への道のり📈 (55kg ➔ 50kg)")
    
    # スプレッドシートからデータを取得
    records = get_weight_data()
    if not records:
        st.info("まだ記録がありません。チャットからデータを入力するとグラフが表示されます。")
        return
        
    df = pd.DataFrame(records)
    
    # 列名の確認（A列: 日付, B列: 入力ログ, C列: AI返信, D列: 体重）
    if '日付' in df.columns and '体重' in df.columns:
        # 体重が空文字の行を除外
        df = df[df['体重'] != ""]
        df = df.dropna(subset=['体重'])
        
        if df.empty:
            st.info("体重の記録がまだありません。")
            return
            
        df['体重'] = pd.to_numeric(df['体重'])
        
        # グラフ作成
        fig = px.line(df, x='日付', y='体重', markers=True, 
                      title='体重の変化', range_y=[48, 56])
        
        # 目標ライン(50kg)
        fig.add_hline(y=50, line_dash="dash", line_color="#27ae60", annotation_text="目標 (50kg)")
        
        # 背景色を透明にして、テーマのCSSに合わせる
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("スプレッドシートの1行目（ヘッダー）に「日付」と「体重」列が見つかりませんでした。")
