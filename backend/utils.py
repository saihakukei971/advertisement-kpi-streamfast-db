"""
ユーティリティ関数
共通処理やヘルパー関数
"""
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import os
from pathlib import Path

# プロジェクトルートディレクトリ取得
ROOT_DIR = Path(__file__).resolve().parent.parent

def get_logger(name: str = __name__) -> logging.Logger:
    """アプリケーションログ設定"""
    # ログディレクトリ作成
    log_dir = ROOT_DIR / "log"
    os.makedirs(log_dir, exist_ok=True)
    
    # 日付ベースのログファイル
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{today}.log"
    
    # ロガー設定
    logger = logging.getLogger(name)
    
    # 既存のハンドラがある場合はスキップ
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)
    
    # ファイルハンドラ設定
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # コンソールハンドラ設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # フォーマット設定
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # ハンドラ追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def validate_csv_format(df: pd.DataFrame) -> Dict[str, Any]:
    """CSVフォーマット検証"""
    required_columns = ['date', 'campaign', 'impressions', 'clicks', 'conversions', 'cost']
    
    # 必須カラム確認
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return {
            "valid": False,
            "error": f"必須カラムがありません: {', '.join(missing_columns)}"
        }
    
    # データ型検証
    try:
        # 日付カラム
        pd.to_datetime(df['date'])
        
        # 数値カラム
        for col in ['impressions', 'clicks', 'conversions', 'cost']:
            pd.to_numeric(df[col])
            
        # NAN値チェック
        null_counts = df[required_columns].isnull().sum().to_dict()
        if sum(null_counts.values()) > 0:
            return {
                "valid": True,
                "warning": f"NULL値が検出されました: {null_counts}"
            }
            
        return {"valid": True}
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"データ型エラー: {str(e)}"
        }

def format_number(value: Union[int, float], precision: int = 0) -> str:
    """数値を3桁区切りでフォーマット"""
    if isinstance(value, (int, float)):
        if precision > 0:
            return f"{value:,.{precision}f}"
        return f"{value:,}"
    return str(value)

def format_percent(value: Union[int, float], precision: int = 2) -> str:
    """パーセント値のフォーマット"""
    if isinstance(value, (int, float)):
        return f"{value * 100:.{precision}f}%"
    return str(value)

def format_currency(value: Union[int, float], currency: str = "¥", precision: int = 0) -> str:
    """通貨のフォーマット"""
    if isinstance(value, (int, float)):
        if precision > 0:
            return f"{currency}{value:,.{precision}f}"
        return f"{currency}{value:,}"
    return str(value)

def get_daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """日別KPI指標を計算"""
    # NULL値を0に置換
    df = df.fillna({
        'impressions': 0,
        'clicks': 0,
        'conversions': 0,
        'cost': 0
    })
    
    # 数値型変換
    for col in ['impressions', 'clicks', 'conversions', 'cost']:
        df[col] = pd.to_numeric(df[col])
    
    # グループ集計
    daily_df = df.groupby('date').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum',
        'cost': 'sum'
    }).reset_index()
    
    # KPI計算
    daily_df['ctr'] = daily_df['clicks'] / daily_df['impressions']
    daily_df['cvr'] = daily_df['conversions'] / daily_df['clicks']
    daily_df['cpa'] = daily_df['cost'] / daily_df['conversions']
    
    # NULL/INF置換
    daily_df = daily_df.replace([float('inf'), float('-inf')], 0)
    daily_df = daily_df.fillna(0)
    
    return daily_df

def get_campaign_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """キャンペーン別KPI指標を計算"""
    # NULL値を0に置換
    df = df.fillna({
        'impressions': 0,
        'clicks': 0,
        'conversions': 0,
        'cost': 0
    })
    
    # 数値型変換
    for col in ['impressions', 'clicks', 'conversions', 'cost']:
        df[col] = pd.to_numeric(df[col])
    
    # グループ集計
    campaign_df = df.groupby('campaign').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum',
        'cost': 'sum'
    }).reset_index()
    
    # KPI計算
    campaign_df['ctr'] = campaign_df['clicks'] / campaign_df['impressions']
    campaign_df['cvr'] = campaign_df['conversions'] / campaign_df['clicks']
    campaign_df['cpa'] = campaign_df['cost'] / campaign_df['conversions']
    
    # NULL/INF置換
    campaign_df = campaign_df.replace([float('inf'), float('-inf')], 0)
    campaign_df = campaign_df.fillna(0)
    
    return campaign_df