@echo off
echo ================================================
echo  advertisement-kpi-streamfast-db - KPI Dashboard
echo ================================================
echo.

REM プロジェクトルートディレクトリ取得
set ROOT_DIR=%~dp0..

REM 仮想環境の確認
if exist "%ROOT_DIR%\venv\Scripts\activate.bat" (
    echo 仮想環境を有効化します...
    call "%ROOT_DIR%\venv\Scripts\activate.bat"
)

REM データベース初期化
echo データベース初期化中...
python "%ROOT_DIR%\backend\db_init.py"

REM FastAPIサーバー起動（バックグラウンド）
echo FastAPIサーバーを起動中...
start /B cmd /c "cd %ROOT_DIR% && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

REM サーバー起動待機
echo サーバー起動待機中...
timeout /t 3 /nobreak > NUL

REM Streamlitダッシュボード起動
echo Streamlitダッシュボードを起動中...
cd "%ROOT_DIR%" && python -m streamlit run frontend\dashboard.py

pause