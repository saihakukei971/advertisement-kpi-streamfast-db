"""
UIコンポーネントモジュール
再利用可能なStreamlitコンポーネント
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
from pathlib import Path

from frontend.config import (
    API_BASE_URL,
    COLORS,
    KPI_METRICS,
    GRAPH_CONFIG,
    TABLE_CONFIG
)
from backend.utils import (
    format_number,
    format_percent,
    format_currency
)

def display_header():
    """ヘッダー表示"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("📊 広告KPI ダッシュボード")
        st.caption("CSVアップロード → SQLite登録 → グラフ可視化 + API連携")
    
    with col2:
        st.markdown(
            f"""
            <div style="text-align: right; margin-top: 20px;">
                <span style="background-color: #f0f2f6; padding: 8px 12px; border-radius: 4px;">
                    {datetime.now().strftime('%Y年%m月%d日')}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

def upload_csv():
    """CSVアップロードコンポーネント"""
    uploaded_file = st.file_uploader(
        "CSVファイルをアップロード",
        type="csv",
        help="date,campaign,impressions,clicks,conversions,cost の形式で準備してください"
    )
    
    if uploaded_file:
        try:
            # CSVファイル読み込み
            df = pd.read_csv(uploaded_file)
            
            # 必須カラム確認
            required_columns = ['date', 'campaign', 'impressions', 'clicks', 'conversions', 'cost']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"必須カラムがありません: {', '.join(missing_columns)}")
                return None
            
            # データ前処理
            df['date'] = pd.to_datetime(df['date'])
            
            # KPI指標計算
            df['ctr'] = df['clicks'] / df['impressions']
            df['cvr'] = df['conversions'] / df['clicks']
            df['cpa'] = df['cost'] / df['conversions']
            
            # 無限値対応
            df = df.replace([float('inf'), float('-inf')], 0)
            df = df.fillna(0)
            
            # DBに登録（API経由）
            with st.spinner("データベースに登録中..."):
                # TODO: API連携実装
                pass
            
            st.success(f"✅ {len(df)}件のデータを読み込みました")
            
            return df
        
        except Exception as e:
            st.error(f"CSVファイル処理エラー: {str(e)}")
            return None
    
    return None

def filter_controls(campaigns: List[str], date_range: Dict[str, str]):
    """フィルターコントロール"""
    st.subheader("📌 データフィルター")
    
    # キャンペーン選択
    campaign = st.selectbox(
        "キャンペーン",
        options=["全て"] + campaigns,
        index=0
    )
    
    # 日付範囲設定
    start_date = date_range.get("start_date")
    end_date = date_range.get("end_date")
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        date_selection = st.date_input(
            "期間",
            value=(start, end),
            min_value=start,
            max_value=end
        )
        
        if isinstance(date_selection, tuple) and len(date_selection) == 2:
            selected_start, selected_end = date_selection
        else:
            selected_start, selected_end = start, end
            
    else:
        selected_start = datetime.now().date() - timedelta(days=30)
        selected_end = datetime.now().date()
        
        date_selection = st.date_input(
            "期間",
            value=(selected_start, selected_end)
        )
        
        if isinstance(date_selection, tuple) and len(date_selection) == 2:
            selected_start, selected_end = date_selection
    
    # フィルターをセッションステートに保存
    st.session_state["filters"] = {
        "campaign": None if campaign == "全て" else campaign,
        "start_date": selected_start.strftime("%Y-%m-%d"),
        "end_date": selected_end.strftime("%Y-%m-%d")
    }
    
    return st.session_state["filters"]

def fetch_kpi_data(filters: Dict[str, Any] = None) -> pd.DataFrame:
    """API経由でKPIデータ取得"""
    if filters is None:
        filters = {}
    
    try:
        # クエリパラメータ設定
        params = {}
        if filters.get("campaign"):
            params["campaign"] = filters["campaign"]
        if filters.get("start_date"):
            params["start_date"] = filters["start_date"]
        if filters.get("end_date"):
            params["end_date"] = filters["end_date"]
        
        # APIリクエスト
        response = requests.get(f"{API_BASE_URL}/kpis", params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # データフレーム変換
            df = pd.DataFrame(data)
            
            # 日付列変換
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
            
            return df
        else:
            st.error(f"APIエラー: {response.status_code} - {response.text}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"データ取得エラー: {str(e)}")
        return pd.DataFrame()

def create_kpi_charts(df: pd.DataFrame):
    """KPI指標グラフ作成"""
    if df.empty:
        st.info("表示するデータがありません")
        return
    
    st.subheader("📊 KPI指標")
    
    # 概要指標表示
    with st.container():
        total_impressions = df["impressions"].sum()
        total_clicks = df["clicks"].sum()
        total_conversions = df["conversions"].sum()
        total_cost = df["cost"].sum()
        
        avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        avg_cvr = total_conversions / total_clicks if total_clicks > 0 else 0
        avg_cpa = total_cost / total_conversions if total_conversions > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "インプレッション",
                format_number(total_impressions),
                delta=None
            )
            
        with col2:
            st.metric(
                "クリック数",
                format_number(total_clicks),
                delta=None
            )
            
        with col3:
            st.metric(
                "コンバージョン",
                format_number(total_conversions),
                delta=None
            )
            
        with col4:
            st.metric(
                "広告費用",
                format_currency(total_cost),
                delta=None
            )
    
    # 日別集計データ
    daily_df = df.groupby("date").agg({
        "impressions": "sum",
        "clicks": "sum",
        "conversions": "sum",
        "cost": "sum"
    }).reset_index()
    
    # KPI計算
    daily_df["ctr"] = daily_df["clicks"] / daily_df["impressions"]
    daily_df["cvr"] = daily_df["conversions"] / daily_df["clicks"]
    daily_df["cpa"] = daily_df["cost"] / daily_df["conversions"]
    
    # グラフ表示
    tab1, tab2, tab3 = st.tabs(["CPA推移", "CVR推移", "CTR推移"])
    
    with tab1:
        fig = px.line(
            daily_df,
            x="date",
            y="cpa",
            title="CPA推移（コンバージョン単価）",
            labels={"date": "日付", "cpa": "CPA"},
            color_discrete_sequence=[KPI_METRICS["CPA"]["color"]],
            height=GRAPH_CONFIG["height"]
        )
        
        fig.update_layout(
            xaxis_title="日付",
            yaxis_title="CPA（円）",
            **GRAPH_CONFIG
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        fig = px.line(
            daily_df,
            x="date",
            y="cvr",
            title="CVR推移（コンバージョン率）",
            labels={"date": "日付", "cvr": "CVR"},
            color_discrete_sequence=[KPI_METRICS["CVR"]["color"]],
            height=GRAPH_CONFIG["height"]
        )
        
        fig.update_layout(
            xaxis_title="日付",
            yaxis_title="CVR（%）",
            **GRAPH_CONFIG
        )
        
        # Y軸をパーセント表示
        fig.update_yaxes(tickformat=".2%")
        
        st.plotly_chart(fig, use_container_width=True)
        
    with tab3:
        fig = px.line(
            daily_df,
            x="date",
            y="ctr",
            title="CTR推移（クリック率）",
            labels={"date": "日付", "ctr": "CTR"},
            color_discrete_sequence=[KPI_METRICS["CTR"]["color"]],
            height=GRAPH_CONFIG["height"]
        )
        
        fig.update_layout(
            xaxis_title="日付",
            yaxis_title="CTR（%）",
            **GRAPH_CONFIG
        )
        
        # Y軸をパーセント表示
        fig.update_yaxes(tickformat=".2%")
        
        st.plotly_chart(fig, use_container_width=True)

def create_campaign_comparison(df: pd.DataFrame):
    """キャンペーン比較グラフ作成"""
    if df.empty or "campaign" not in df.columns:
        return
    
    # キャンペーン別に集計
    campaign_df = df.groupby("campaign").agg({
        "impressions": "sum",
        "clicks": "sum",
        "conversions": "sum",
        "cost": "sum"
    }).reset_index()
    
    # KPI計算
    campaign_df["ctr"] = campaign_df["clicks"] / campaign_df["impressions"]
    campaign_df["cvr"] = campaign_df["conversions"] / campaign_df["clicks"]
    campaign_df["cpa"] = campaign_df["cost"] / campaign_df["conversions"]
    
    st.subheader("📊 キャンペーン比較")
    
    tabs = st.tabs(["CPA比較", "CVR比較", "CTR比較", "コスト比較"])
    
    with tabs[0]:
        fig = px.bar(
            campaign_df,
            x="campaign",
            y="cpa",
            title="キャンペーン別CPA",
            color="campaign",
            color_discrete_sequence=COLORS["graph_palette"],
            height=400
        )
        
        fig.update_layout(
            xaxis_title="キャンペーン",
            yaxis_title="CPA（円）",
            **GRAPH_CONFIG
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        fig = px.bar(
            campaign_df,
            x="campaign",
            y="cvr",
            title="キャンペーン別CVR",
            color="campaign",
            color_discrete_sequence=COLORS["graph_palette"],
            height=400
        )
        
        fig.update_layout(
            xaxis_title="キャンペーン",
            yaxis_title="CVR（%）",
            **GRAPH_CONFIG
        )
        
        fig.update_yaxes(tickformat=".2%")
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        fig = px.bar(
            campaign_df,
            x="campaign",
            y="ctr",
            title="キャンペーン別CTR",
            color="campaign",
            color_discrete_sequence=COLORS["graph_palette"],
            height=400
        )
        
        fig.update_layout(
            xaxis_title="キャンペーン",
            yaxis_title="CTR（%）",
            **GRAPH_CONFIG
        )
        
        fig.update_yaxes(tickformat=".2%")
        
        st.plotly_chart(fig, use_container_width=True)
        
    with tabs[3]:
        fig = px.bar(
            campaign_df,
            x="campaign",
            y="cost",
            title="キャンペーン別コスト",
            color="campaign",
            color_discrete_sequence=COLORS["graph_palette"],
            height=400
        )
        
        fig.update_layout(
            xaxis_title="キャンペーン",
            yaxis_title="コスト（円）",
            **GRAPH_CONFIG
        )
        
        fig.update_yaxes(tickformat=",")
        
        st.plotly_chart(fig, use_container_width=True)

def display_data_table(df: pd.DataFrame):
    """データテーブル表示"""
    if df.empty:
        return
    
    st.subheader("📋 データテーブル")
    
    # テーブルソート用
    if "date" in df.columns:
        df = df.sort_values("date", ascending=False)
    
    # NaN対応
    df_display = df.fillna(0)
    
    # 表示列定義
    visible_columns = [col["name"] for col in TABLE_CONFIG["columns"]]
    
    # 表示データ準備
    display_df = df_display.copy()
    
    # 列ラベル変更
    column_mapping = {col["name"]: col["label"] for col in TABLE_CONFIG["columns"]}
    display_df = display_df.rename(columns=column_mapping)
    
    # 表示形式設定
    formatters = {}
    for col in TABLE_CONFIG["columns"]:
        if col["format"] == "number":
            display_df[col["label"]] = display_df[col["label"]].apply(format_number)
        elif col["format"] == "percent":
            display_df[col["label"]] = display_df[col["label"]].apply(format_percent)
        elif col["format"] == "currency":
            display_df[col["label"]] = display_df[col["label"]].apply(format_currency)
        elif col["format"] == "date" and "date" in display_df.columns:
            display_df[col["label"]] = display_df[col["label"]].dt.strftime("%Y-%m-%d")
    
    # 表示列選択
    visible_labels = [column_mapping.get(col, col) for col in visible_columns if col in df.columns]
    
    # テーブル表示
    st.dataframe(
        display_df[visible_labels],
        use_container_width=True,
        height=400
    )
    
    # CSV/Excelダウンロードボタン
    col1, col2 = st.columns(2)
    
    with col1:
        # CSVダウンロード
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="CSVダウンロード",
            data=csv,
            file_name=f"ad_kpi_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excelダウンロード
        buffer = pd.io.excel.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        excel_data = buffer.getvalue()
        st.download_button(
            label="Excelダウンロード",
            data=excel_data,
            file_name=f"ad_kpi_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )