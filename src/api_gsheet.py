import os
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_sheet():
    """スプレッドシートへの接続を行い、ワークシートオブジェクトを返す"""
    import json
    
    # 1. スプレッドシートキーの取得 (Secrets 優先)
    try:
        SPREADSHEET_KEY = st.secrets["SPREADSHEET_KEY"]
    except Exception:
        SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")
        
    if not SPREADSHEET_KEY or SPREADSHEET_KEY == "your_spreadsheet_key_here":
        raise ValueError("SPREADSHEET_KEY が設定されていません。")

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # 2. 認証情報の取得
    try:
        # Streamlit Secrets に JSON 文字列が登録されている場合
        if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in st.secrets:
            creds_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
            credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
        # あるいはTOML辞書として登録されている場合
        elif "gcp_service_account" in st.secrets:
            creds_info = dict(st.secrets["gcp_service_account"])
            credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
        else:
            raise KeyError()
    except Exception:
        # ローカル環境のファイルからの読み込み
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "rina-diet-app.json")
        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"サービスアカウントキーが見つかりません: {creds_path}")
        credentials = Credentials.from_service_account_file(creds_path, scopes=scope)

    gc = gspread.authorize(credentials)
    return gc.open_by_key(SPREADSHEET_KEY).sheet1

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
