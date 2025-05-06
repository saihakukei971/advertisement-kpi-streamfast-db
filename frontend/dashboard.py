"""
Streamlit ダッシュボード
広告KPIの可視化UIを提供
"""
import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time
import threading
import subprocess

# 相対インポート
from frontend.config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_ICON,
    API_BASE_URL,
    COLORS,
    KPI_METRICS,
    SAMPLE_CSV_PATH
)
from frontend.components import (
    display_header,
    upload_csv,
    filter_controls,
    fetch_kpi_data,
    create_kpi_charts,
    create_campaign_comparison,
    display_data_table
)
from backend.db_init import upload_csv_to_db
from backend.utils import get_logger

# ロガー設定
logger = get_logger(__name__)

# ページ設定
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# スタイルシート適用
st.markdown(
    f"""
    <style>
    .main .block-container {{
        padding-top: 2rem;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS["primary"]};
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

def check_api_availability():
    """APIサーバーの接続確認"""
    try:
        response = requests.get(f"{API_BASE_URL}/kpis/campaigns", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

def get_campaigns_list():
    """キャンペーン一覧取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/kpis/campaigns")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        logger.error(f"キャンペーン一覧取得エラー: {str(e)}")
        return []

def get_date_range():
    """日付範囲取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/kpis/date-range")
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        logger.error(f"日付範囲取得エラー: {str(e)}")
        return {}

def start_fastapi_server():
    """FastAPIサーバーをバックグラウンドで起動"""
    try:
        # カレントディレクトリを取得
        root_dir = Path(__file__).resolve().parent.parent

        # サーバー起動コマンド
        cmd = [
            "uvicorn",
            "backend.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ]

        # サブプロセスでサーバー起動
        process = subprocess.Popen(
            cmd,
            cwd=root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # サーバー起動ログ
        logger.info("FastAPI サーバー起動中...")

        # サーバー起動待機
        for _ in range(5):
            if check_api_availability():
                logger.info("FastAPI サーバー起動完了")
                return True
            time.sleep(1)

        logger.warning("FastAPI サーバー起動タイムアウト")
        return False

    except Exception as e:
        logger.error(f"FastAPI サーバー起動エラー: {str(e)}")
        return False

def main():
    """メイン処理"""
    # ヘッダー表示
    display_header()

    # セッション状態初期化
    if "data_loaded" not in st.session_state:
        st.session_state["data_loaded"] = False

    if "filters" not in st.session_state:
        st.session_state["filters"] = {}

    # サイドバー設定
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3698/3698156.png", width=100)
        st.title("メニュー")

        # CSVアップロード
        st.subheader("📤 CSVアップロード")
        uploaded_file = st.file_uploader(
            "CSVファイルを選択",
            type="csv",
            help="date,campaign,impressions,clicks,conversions,cost の形式"
        )

        if uploaded_file:
            try:
                # メモリ上でCSVファイル読み込み
                df = pd.read_csv(uploaded_file)

                # 必須カラム確認
                required_columns = ['date', 'campaign', 'impressions', 'clicks', 'conversions', 'cost']
                missing_columns = [col for col in required_columns if col not in df.columns]

                if missing_columns:
                    st.error(f"必須カラムがありません: {', '.join(missing_columns)}")
                else:
                    # DBにアップロード
                    with st.spinner("データベースに登録中..."):
                        # アップロードモード選択
                        mode = st.radio(
                            "アップロードモード",
                            options=["追加", "置換"],
                            index=0,
                            horizontal=True
                        )

                        if st.button("登録実行", type="primary"):
                            try:
                                # CSVをDBに登録
                                replace = (mode == "置換")
                                rows = upload_csv_to_db(uploaded_file, replace)

                                st.success(f"✅ {rows}件のデータを登録しました")

                                # セッション状態更新
                                st.session_state["data_loaded"] = True

                                # 画面リロード
                                st.rerun()

                            except Exception as e:
                                st.error(f"CSVアップロードエラー: {str(e)}")

            except Exception as e:
                st.error(f"CSVファイル読み込みエラー: {str(e)}")

        # デモCSV生成
        st.subheader("🧪 デモデータ")
        if st.button("サンプルCSVを生成"):
            try:
                # サンプルデータ作成
                num_days = 60
                campaigns = ["Google Ads", "Yahoo Ads", "Facebook Ads", "Instagram Ads", "Twitter Ads"]

                data = []
                end_date = datetime.now().date()

                for i in range(num_days):
                    current_date = end_date - timedelta(days=i)
                    date_str = current_date.strftime("%Y-%m-%d")

                    for campaign in campaigns:
                        # 乱数でデータ生成
                        impressions = np.random.randint(5000, 50000)
                        clicks = np.random.randint(100, int(impressions * 0.1))
                        conversions = np.random.randint(1, int(clicks * 0.2))
                        cost = np.random.randint(5000, 100000)

                        data.append({
                            "date": date_str,
                            "campaign": campaign,
                            "impressions": impressions,
                            "clicks": clicks,
                            "conversions": conversions,
                            "cost": cost
                        })

                # CSVファイル作成
                df = pd.DataFrame(data)

                # サンプルCSVパス
                sample_path = Path(SAMPLE_CSV_PATH)
                os.makedirs(sample_path.parent, exist_ok=True)

                # CSVファイル保存
                df.to_csv(sample_path, index=False)

                # DBに登録
                upload_csv_to_db(sample_path, replace=True)

                st.success(f"✅ サンプルデータ({len(data)}件)を生成してDBに登録しました")

                # セッション状態更新
                st.session_state["data_loaded"] = True

                # 画面リロード
                st.rerun()

            except Exception as e:
                st.error(f"サンプルデータ生成エラー: {str(e)}")

        # APIドキュメント
        st.subheader("🔌 API情報")
        st.write("以下のエンドポイントでKPIデータにアクセスできます：")
        st.code("GET /api/kpis - 全データ取得")
        st.code("GET /api/kpis?campaign=Google Ads - キャンペーン指定")
        st.code("GET /api/kpis/metrics - 指標サマリー取得")

        # Swagger UI
        st.markdown(f"[API ドキュメント (Swagger UI)]({API_BASE_URL.replace('/api', '')}/docs)")

    # メイン画面
    if not check_api_availability():
        st.warning("🔄 API サーバーに接続できません。サーバーを起動中...")

        # APIサーバー起動
        if start_fastapi_server():
            st.success("✅ API サーバー起動完了")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ API サーバー起動失敗。もう一度試すか、手動でサーバーを起動してください。")
            st.code("uvicorn backend.main:app --reload")
            st.stop()

    # キャンペーン一覧と日付範囲取得
    campaigns = get_campaigns_list()
    date_range = get_date_range()

    if not campaigns:
        st.info("📊 データが登録されていません。サイドバーからCSVをアップロードするか、サンプルデータを生成してください。")
        st.stop()

    # フィルター設定
    st.write("---")
    filters = filter_controls(campaigns, date_range)
    st.write("---")

    # データ取得
    with st.spinner("データ取得中..."):
        df = fetch_kpi_data(filters)

    if df.empty:
        st.info("🔍 条件に一致するデータがありません。フィルターを変更してください。")
        st.stop()

    # KPI指標グラフ作成
    create_kpi_charts(df)

    # キャンペーン比較
    if not filters.get("campaign"):
        create_campaign_comparison(df)

    # データテーブル表示
    display_data_table(df)

    # フッター表示
    st.write("---")
    st.caption(
        "© 2025 advertisement-kpi-streamfast-db | "
        "Streamlit + FastAPI + SQLite による広告KPI分析ツール"
    )

if __name__ == "__main__":
    main()