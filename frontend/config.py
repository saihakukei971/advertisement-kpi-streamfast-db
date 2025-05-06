"""
UI設定モジュール
Streamlitアプリケーションの設定値
"""
from typing import Dict, Any, List
from pathlib import Path

# プロジェクトルートディレクトリ取得
ROOT_DIR = Path(__file__).resolve().parent.parent

# アプリ設定
APP_TITLE = "📊 広告KPI ダッシュボード"
APP_SUBTITLE = "CSV＋DB＋API連携分析ツール"
APP_ICON = "📈"

# API接続設定
API_BASE_URL = "http://localhost:8000/api"

# テーマカラー
COLORS = {
    "primary": "#1E88E5",
    "secondary": "#26A69A",
    "background": "#F5F7F9",
    "text": "#333333",
    "graph_palette": [
        "#1E88E5",  # 青
        "#26A69A",  # ティール
        "#7CB342",  # 緑
        "#FFA000",  # オレンジ
        "#E53935",  # 赤
        "#8E24AA",  # 紫
    ]
}

# KPI指標設定
KPI_METRICS = {
    "CTR": {
        "name": "クリック率",
        "description": "インプレッション数に対するクリック数の割合",
        "formula": "clicks / impressions",
        "format": "percent",
        "color": COLORS["graph_palette"][0],
        "order": 1,
    },
    "CVR": {
        "name": "コンバージョン率",
        "description": "クリック数に対するコンバージョン数の割合",
        "formula": "conversions / clicks",
        "format": "percent",
        "color": COLORS["graph_palette"][1],
        "order": 2,
    },
    "CPA": {
        "name": "獲得単価",
        "description": "コンバージョン1件あたりのコスト",
        "formula": "cost / conversions",
        "format": "currency",
        "color": COLORS["graph_palette"][2],
        "order": 3,
    }
}

# グラフ設定
GRAPH_CONFIG = {
    "height": 400,
    "margin": {"l": 50, "r": 20, "t": 50, "b": 50},
    "plot_bgcolor": "#FFFFFF",
    "paper_bgcolor": "#FFFFFF",
    "font": {"color": COLORS["text"]},
    "colorway": COLORS["graph_palette"],
}

# テーブル表示設定
TABLE_CONFIG = {
    "columns": [
        {"name": "date", "label": "日付", "format": "date"},
        {"name": "campaign", "label": "キャンペーン", "format": "text"},
        {"name": "impressions", "label": "インプレッション", "format": "number"},
        {"name": "clicks", "label": "クリック数", "format": "number"},
        {"name": "conversions", "label": "コンバージョン", "format": "number"},
        {"name": "cost", "label": "コスト", "format": "currency"},
        {"name": "ctr", "label": "CTR", "format": "percent"},
        {"name": "cvr", "label": "CVR", "format": "percent"},
        {"name": "cpa", "label": "CPA", "format": "currency"}
    ],
    "page_size": 10,
}

# サンプルCSVパス
SAMPLE_CSV_PATH = ROOT_DIR / "data" / "sample_kpi.csv"

# DB設定
DB_PATH = ROOT_DIR / "kpi.db"

# ログ設定
LOG_DIR = ROOT_DIR / "log"