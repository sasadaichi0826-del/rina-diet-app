import streamlit as st
import os

def load_css(theme_name: str, bg_color="#0a0a1a", text_color="#FFD700"):
    """
    指定されたテーマ名のCSSファイルを読み込み、Streamlitに適用する
    """
    css_file = "style_devil.css" if theme_name == "devil" else "style_relax.css"
    if theme_name == "tesla":
        css_file = "style_tesla.css"
        
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", css_file)
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            base_css = f.read()
            
        custom_css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Mochiy+Pop+P+One&family=Zen+Maru+Gothic:wght@400;700&display=swap');
        
        {base_css}
        
        .stApp {{
            background: {bg_color} !important;
            color: {text_color} !important;
            font-family: 'Mochiy Pop P One', 'Zen Maru Gothic', sans-serif !important;
        }}
        
        h1, h2, h3, h4, .stMarkdown p strong, .stMarkdown p span, label {{
            color: {text_color} !important;
            font-family: 'Mochiy Pop P One', 'Zen Maru Gothic', sans-serif !important;
        }}
        
        div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"], .stChatMessage {{
            font-family: 'Zen Maru Gothic', sans-serif !important;
        }}
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)
