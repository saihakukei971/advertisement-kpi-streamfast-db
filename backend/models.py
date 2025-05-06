"""
SQLAlchemyモデル定義
広告KPIデータのデータベースモデルを定義
"""
from sqlalchemy import Column, Integer, String, Float, Date, Index, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Dict, Any, Optional

Base = declarative_base()

class KPI(Base):
    """広告KPIデータモデル"""
    __tablename__ = "kpis"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    campaign = Column(String, nullable=False)
    impressions = Column(Integer, nullable=False)
    clicks = Column(Integer, nullable=False)
    conversions = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)

    # パフォーマンス向上のためのインデックス
    __table_args__ = (
        Index('idx_date', 'date'),
        Index('idx_campaign', 'campaign'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """モデルを辞書に変換"""
        return {
            "id": self.id,
            "date": self.date.isoformat() if isinstance(self.date, date) else self.date,
            "campaign": self.campaign,
            "impressions": self.impressions,
            "clicks": self.clicks,
            "conversions": self.conversions,
            "cost": self.cost,
            "ctr": round(self.clicks / self.impressions, 4) if self.impressions > 0 else 0,
            "cvr": round(self.conversions / self.clicks, 4) if self.clicks > 0 else 0,
            "cpa": round(self.cost / self.conversions, 2) if self.conversions > 0 else 0
        }

    @staticmethod
    def get_campaigns(session: Session) -> List[str]:
        """全キャンペーン名を取得"""
        return [r[0] for r in session.query(KPI.campaign).distinct().all()]

    @staticmethod
    def get_date_range(session: Session) -> Dict[str, str]:
        """データの日付範囲を取得"""
        min_date = session.query(func.min(KPI.date)).scalar()
        max_date = session.query(func.max(KPI.date)).scalar()
        return {
            "start_date": min_date.isoformat() if min_date else None,
            "end_date": max_date.isoformat() if max_date else None
        }

    @staticmethod
    def get_metrics_summary(session: Session, campaign: Optional[str] = None) -> Dict[str, Any]:
        """KPI指標のサマリーを計算"""
        query = session.query(
            func.sum(KPI.impressions).label("total_impressions"),
            func.sum(KPI.clicks).label("total_clicks"),
            func.sum(KPI.conversions).label("total_conversions"),
            func.sum(KPI.cost).label("total_cost")
        )

        if campaign:
            query = query.filter(KPI.campaign == campaign)

        result = query.first()

        # 結果が存在する場合のみ計算
        if result and result.total_impressions:
            total_impressions = result.total_impressions or 0
            total_clicks = result.total_clicks or 0
            total_conversions = result.total_conversions or 0
            total_cost = result.total_cost or 0

            # KPI指標計算
            ctr = round(total_clicks / total_impressions, 4) if total_impressions > 0 else 0
            cvr = round(total_conversions / total_clicks, 4) if total_clicks > 0 else 0
            cpa = round(total_cost / total_conversions, 2) if total_conversions > 0 else 0

            return {
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "total_cost": total_cost,
                "ctr": ctr,
                "cvr": cvr,
                "cpa": cpa
            }

        return {
            "total_impressions": 0,
            "total_clicks": 0,
            "total_conversions": 0,
            "total_cost": 0,
            "ctr": 0,
            "cvr": 0,
            "cpa": 0
        }