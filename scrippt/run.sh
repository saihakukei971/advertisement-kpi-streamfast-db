#!/bin/bash

echo "================================================"
echo " advertisement-kpi-streamfast-db - KPI Dashboard"
echo "================================================"
echo ""

# プロジェクトルートディレクトリ取得
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 仮想環境の確認
if [ -f "${ROOT_DIR}/venv/bin/activate" ]; then
    echo "仮想環境を有効化します..."
    source "${ROOT_DIR}/venv/bin/activate"
fi

# データベース初期化
echo "データベース初期化中..."
python "${ROOT_DIR}/backend/db_init.py"

# FastAPIサーバー起動（バックグラウンド）
echo "FastAPIサーバーを起動中..."
cd "${ROOT_DIR}" && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

# サーバー起動待機
echo "サーバー起動待機中..."
sleep 3

# Streamlitダッシュボード起動
echo "Streamlitダッシュボードを起動中..."
cd "${ROOT_DIR}" && python -m streamlit run frontend/dashboard.py

# 終了時にAPIサーバーも終了
kill $API_PID