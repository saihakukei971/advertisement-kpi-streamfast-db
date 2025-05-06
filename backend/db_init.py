"""
DB初期化モジュール
CSVファイルをSQLiteデータベースに登録
"""
import pandas as pd
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime
from typing import Optional, Union

from backend.models import Base, KPI

# プロジェクトルートディレクトリ取得
ROOT_DIR = Path(__file__).resolve().parent.parent

# ログ設定
def setup_logging() -> None:
    """ロギング設定"""
    log_dir = ROOT_DIR / "log"
    os.makedirs(log_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{today}.log"

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def init_db(csv_path: Optional[Union[str, Path]] = None) -> None:
    """
    CSVファイルからデータベースを初期化

    Args:
        csv_path: CSVファイルパス。Noneの場合はデフォルトのサンプルファイルを使用
    """
    setup_logging()

    # デフォルトCSVパス
    if csv_path is None:
        csv_path = ROOT_DIR / "data" / "sample_kpi.csv"
    elif isinstance(csv_path, str):
        csv_path = Path(csv_path)

    # CSVファイル存在確認
    if not csv_path.exists():
        error_msg = f"CSVファイルが見つかりません: {csv_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)

    # DB接続
    db_path = ROOT_DIR / "kpi.db"
    engine = create_engine(f"sqlite:///{db_path}")

    # テーブル作成
    Base.metadata.create_all(engine)

    try:
        # CSVからデータフレーム読み込み
        df = pd.read_csv(csv_path)

        # データ前処理
        df["date"] = pd.to_datetime(df["date"]).dt.date

        # NULL値チェック
        null_check = df.isnull().sum().sum()
        if null_check > 0:
            logging.warning(f"NULL値が{null_check}個検出されました。")
            # NULL値を適切に処理（0で埋めるなど）
            df = df.fillna({
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "cost": 0
            })

        # データ型変換
        df["impressions"] = df["impressions"].astype(int)
        df["clicks"] = df["clicks"].astype(int)
        df["conversions"] = df["conversions"].astype(int)
        df["cost"] = df["cost"].astype(float)

        # DBに保存
        df.to_sql("kpis", con=engine, if_exists="replace", index=False)

        # ログ出力
        logging.info(f"CSV → DB登録完了。ファイル: {csv_path.name}, 行数: {len(df)}")
        print(f"✅ データベース初期化完了。{len(df)}件のデータを登録しました。")

    except Exception as e:
        error_msg = f"DB初期化エラー: {str(e)}"
        logging.error(error_msg)
        print(f"❌ エラー: {error_msg}")
        raise

def upload_csv_to_db(csv_file: Union[str, Path, bytes], replace: bool = False) -> int:
    """
    CSVファイル/バイトデータをアップロードしてDBに追加

    Args:
        csv_file: CSVファイルパスまたはバイトデータ
        replace: Trueの場合は既存データを置換、Falseの場合は追加

    Returns:
        登録された行数
    """
    setup_logging()

    # DB接続
    db_path = ROOT_DIR / "kpi.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)

    try:
        # ファイルタイプに応じてデータフレーム読み込み
        if isinstance(csv_file, (str, Path)):
            df = pd.read_csv(csv_file)
        else:
            df = pd.read_csv(csv_file)

        # データ前処理
        df["date"] = pd.to_datetime(df["date"]).dt.date

        # NULL値チェック
        null_check = df.isnull().sum().sum()
        if null_check > 0:
            logging.warning(f"NULL値が{null_check}個検出されました。")
            # NULL値を適切に処理
            df = df.fillna({
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "cost": 0
            })

        # データ型変換
        df["impressions"] = df["impressions"].astype(int)
        df["clicks"] = df["clicks"].astype(int)
        df["conversions"] = df["conversions"].astype(int)
        df["cost"] = df["cost"].astype(float)

        # DBに保存
        if_exists = "replace" if replace else "append"
        df.to_sql("kpis", con=engine, if_exists=if_exists, index=False)

        # ログ出力
        file_name = csv_file if isinstance(csv_file, str) else "uploaded_file"
        logging.info(f"CSV → DB登録完了。ファイル: {file_name}, 行数: {len(df)}, モード: {if_exists}")

        return len(df)

    except Exception as e:
        error_msg = f"CSVアップロードエラー: {str(e)}"
        logging.error(error_msg)
        raise

if __name__ == "__main__":
    init_db()