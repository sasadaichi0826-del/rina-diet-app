import os
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_sheet():
    """環境変数の認証情報を使用してワークシートを取得する"""
    try:
        cred_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        sheet_key = os.getenv("SPREADSHEET_KEY")
        
        if not cred_file or not sheet_key:
            raise ValueError(".envの GOOGLE_APPLICATION_CREDENTIALS または SPREADSHEET_KEY が未設定です。")
            
        credentials = Credentials.from_service_account_file(cred_file, scopes=SCOPES)
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(sheet_key)
        return spreadsheet.sheet1
    except Exception as e:
        print(f"【Auth/Connection Error】: {e}")
        raise e

def add_record(date_str, time_str, food_str, calories, ai_message, weight):
    """
    [A: 日付, B: 時間, C: 内容, D: カロリー, E: AI返信, F: 体重] の6カラム形式に保存する。
    """
    try:
        ws = get_sheet()
        
        row_data = [
            date_str,
            time_str if time_str else "",
            food_str if food_str else "",
            calories if calories else "",
            ai_message,
            weight if weight else ""
        ]
        
        ws.append_row(row_data)
        return True
        
    except Exception as e:
        error_msg = f"Spreadsheet書き込みエラー(append_row): {e}"
        print(error_msg)
        st.error(error_msg)
        return False

def get_weight_data():
    """全レコードを取得して辞書のリストとして返す。"""
    try:
        ws = get_sheet()
        return ws.get_all_records()
    except Exception as e:
        error_msg = f"Spreadsheet読み込みエラー(get_all_records): {e}"
        print(error_msg)
        st.error(error_msg)
        return []

def update_all_records(df):
    """データフレームを受け取り、スプレッドシート全体を上書きする双方向同期関数"""
    try:
        ws = get_sheet()
        ws.clear()
        data = [df.columns.values.tolist()] + df.values.tolist()
        ws.update('A1', data)
        return True
    except Exception as e:
        print(f"Spreadsheet一括更新エラー: {e}")
        return False

# --- デバッグ用機能 ---
def run_connection_test():
    """サイドバーから実行される接続・読み書きテスト"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 デバッグテスト実行結果")
    
    # 1. 接続テスト
    try:
        ws = get_sheet()
        st.sidebar.success("✅ 1. アクセス権限テスト成功")
    except Exception as e:
        st.sidebar.error(f"❌ 1. アクセス権限エラー: {e}")
        return
        
    # 2. 書き込みテスト
    try:
        # A列: 日付, B列: 時間, C列: 内容, D列: カロリー, E列: AI返信, F列: 体重
        ws.append_row(["2026-01-01", "12:00", "接続テスト", "100", "テスト返信です", 55.0])
        st.sidebar.success("✅ 2. テストデータの書き込み成功")
    except Exception as e:
        st.sidebar.error(f"❌ 2. 書き込みテストエラー: {e}")
        return
        
    # 3. 読み取りテスト
    try:
        data = ws.get_all_records()
        st.sidebar.success("✅ 3. データの読み取り成功")
        with st.sidebar.expander("取得したデータ(最大3件)"):
            st.write(data[:3])
    except Exception as e:
        st.sidebar.error(f"❌ 3. 読み取りテストエラー: {e}")
        return
