import os
import json
import datetime
import streamlit as st
import google.generativeai as genai

def init_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY")
        
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY が設定されていません。")
    genai.configure(api_key=api_key)

def get_diet_response(chat_history: list) -> dict:
    """
    チャット履歴全体を見て不足情報を補完し、JSONフォーマットの辞書を返す。
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "assets", "prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
            
        # 履歴を文字列として組み立てて文脈を渡す
        now = datetime.datetime.now()
        history_text = f"【現在の日時: {now.strftime('%Y/%m/%d %H:%M')}】\n※「今日」や「昨日」、「さっき」などの相対的な日時は、この現在日時を基準に yyyy/mm/dd や HH:MM 形式に正しく変換してください。\n\n"
        history_text += "【これまでの会話履歴（文脈の参考にして不足要素を推測してください）】\n"
        for msg in chat_history[-6:]: # 直近6件を参照
            role = "AI" if msg["role"] == "assistant" else "里奈"
            text = msg["content"]
            history_text += f"{role}: {text}\n"
            
        full_text = f"{system_prompt}\n\n{history_text}\nいまユーザーが入力した最新の発言を含め、上記の文脈からJSONを生成してください。"
        
        response = model.generate_content(full_text)
        
        # ```json ... ``` のようなマークダウンが返ってきた場合のクレンジング
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        data = json.loads(raw_text.strip())
        return data
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return {
            "status": "error",
            "reply_message": f"あちゃ！エラーが発生しちゃったみたい！ (Error: {e})",
            "extracted_date": "",
            "extracted_time": "",
            "extracted_food": "",
            "extracted_calories": 0
        }
