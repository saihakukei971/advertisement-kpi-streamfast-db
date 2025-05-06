"""
FastAPIアプリケーション
KPIデータのAPIエンドポイント提供
"""
from fastapi import FastAPI, Query, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from datetime import date, datetime
import pandas as pd
from pathlib import Path

from backend.models import Base, KPI
from backend.utils import get_logger

# ロガー設定
logger = get_logger(__name__)

# プロジェクトルートディレクトリ取得
ROOT_DIR = Path(__file__).resolve().parent.parent

# アプリケーション作成
app = FastAPI(
    title="広告KPI API",
    description="広告キャンペーンのKPIデータ提供APIサーバー",
    version="1.0.0"
)

# CORS設定（開発環境用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース設定
DB_PATH = ROOT_DIR / "kpi.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# データベース接続依存関数
def get_db():
    """DB接続セッションを提供"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# テーブル作成
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "広告KPI APIサーバー",
        "documentation": "/docs",
        "version": "1.0.0"
    }

@app.get("/api/kpis", response_model=List[Dict[str, Any]])
async def get_kpis(
    campaign: Optional[str] = Query(None, description="キャンペーン名でフィルタ"),
    start_date: Optional[str] = Query(None, description="開始日（YYYY-MM-DD形式）"),
    end_date: Optional[str] = Query(None, description="終了日（YYYY-MM-DD形式）"),
    db: Session = Depends(get_db)
):
    """KPIデータ取得"""
    try:
        query = select(KPI)

        # フィルタ適用
        if campaign:
            query = query.filter(KPI.campaign == campaign)

        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(KPI.date >= start)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="開始日の形式が不正です。YYYY-MM-DD形式で指定してください。"
                )

        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(KPI.date <= end)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="終了日の形式が不正です。YYYY-MM-DD形式で指定してください。"
                )

        # データ取得
        results = db.execute(query).scalars().all()

        # 結果をディクショナリに変換
        data = [kpi.to_dict() for kpi in results]

        # ログ出力
        logger.info(f"KPIデータ取得: {len(data)}件, フィルタ: campaign={campaign}, 期間={start_date}～{end_date}")

        return data

    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"データ取得エラー: {str(e)}"
        )

@app.get("/api/kpis/campaigns", response_model=List[str])
async def get_campaigns(db: Session = Depends(get_db)):
    """キャンペーン一覧取得"""
    try:
        campaigns = KPI.get_campaigns(db)
        logger.info(f"キャンペーン一覧取得: {len(campaigns)}件")
        return campaigns
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"キャンペーン一覧取得エラー: {str(e)}"
        )

@app.get("/api/kpis/date-range", response_model=Dict[str, Any])
async def get_date_range(db: Session = Depends(get_db)):
    """日付範囲取得"""
    try:
        date_range = KPI.get_date_range(db)
        logger.info(f"日付範囲取得: {date_range}")
        return date_range
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"日付範囲取得エラー: {str(e)}"
        )

@app.get("/api/kpis/metrics", response_model=Dict[str, Any])
async def get_metrics(
    campaign: Optional[str] = Query(None, description="キャンペーン名でフィルタ"),
    db: Session = Depends(get_db)
):
    """KPI指標サマリー取得"""
    try:
        metrics = KPI.get_metrics_summary(db, campaign)
        logger.info(f"KPI指標サマリー取得: campaign={campaign}")
        return metrics
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KPI指標サマリー取得エラー: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)