# 📊 advertisement-kpi-streamfast-db

## 📝 プロジェクト概要

**advertisement-kpi-streamfast-db**は広告KPI（CPA, CVR, CTR等）を分析・可視化するための統合ダッシュボードソリューションです。CSV形式の広告データをSQLiteデータベースに取り込み、Streamlitでインタラクティブに可視化し、さらにFastAPIでREST APIとしても提供します。

実務で必要な広告効果測定のワークフローをエンドツーエンドで実装し、広告担当者が毎日のレポート作成や意思決定に即活用できるツールです。広告代理店や企業のマーケティング部門での日常業務を効率化し、データドリブンな意思決定をサポートします。

![メインダッシュボード](https://i.imgur.com/5BdjHBU.png)

## 🛠️ 使用技術

- **フロントエンド**: Streamlit (v1.26.0) - インタラクティブなデータアプリ構築
- **バックエンド**: FastAPI (v0.100.0) - 高速なAPIフレームワーク
- **データベース**: SQLite + SQLAlchemy (v2.0.20) - 軽量DB + ORM
- **データ処理**: pandas (v2.0.3), NumPy (v1.24.4) - データ操作・分析
- **可視化**: plotly (v5.16.1) - インタラクティブグラフ
- **その他**:
  - uvicorn: ASGIサーバー
  - python-multipart: マルチパートフォーム処理
  - requests: HTTP通信
  - openpyxl: Excel読み書き

## 🔄 処理の流れ

```
+----------------+     +----------------+     +----------------+
| CSVファイル     | --> | データ変換処理  | --> | SQLiteデータベース |
+----------------+     +----------------+     +----------------+
                                               |
                                               v
+-----------------+     +----------------+     +----------------+
| データエクスポート | <-- | Streamlit UI   | <-- | FastAPI バックエンド |
+-----------------+     +----------------+     +----------------+
                        |                      |
                        v                      v
                +----------------+     +----------------+
                | 可視化グラフ    |     | 外部連携API    |
                +----------------+     +----------------+
```

### 詳細な処理ステップ

1. **データ取り込み**:
   - CSVファイルをStreamlit UIまたはAPIからアップロード
   - 広告プラットフォーム（Google Ads、Facebookなど）からのデータ形式に対応

2. **データ処理**:
   - pandas/NumPyによるデータ前処理と変換
   - 日付フォーマット、NULL値処理、型変換を自動実行
   - CTR、CVR、CPAなどのKPI指標を自動計算

3. **データ保存**:
   - SQLAlchemyを用いてSQLiteデータベースに保存
   - ORM（オブジェクトリレーショナルマッピング）によるデータアクセス
   - 追加/置換モードをサポート

4. **API提供**:
   - FastAPIによるRESTful API提供
   - 各種フィルタリングオプション（キャンペーン、日付範囲）
   - OpenAPI仕様（Swagger UI）による自動ドキュメント化
   - CORSサポート（クロスオリジンリクエスト）

5. **データ可視化**:
   - Streamlitによるインタラクティブダッシュボード
   - plotlyによる動的グラフ表示
   - フィルタリングとリアルタイム更新
   - CSVおよびExcel形式でのエクスポート

## ✨ 特徴・工夫した点

### 1. アーキテクチャ設計

- **モジュラー構造**: バックエンド/フロントエンド/データ層の明確な分離で保守性向上
- **RESTful API設計**: 拡張性を考慮したエンドポイント設計で他システムとの連携が容易
- **ORM活用**: SQLAlchemy による型安全なデータアクセスで安全性とパフォーマンスを両立
- **マイクロサービス的アプローチ**: 各コンポーネントが疎結合で、部分的な更新や再利用が容易

### 2. パフォーマンス最適化

- **インデックス定義**: 頻繁にアクセスされるキャンペーン名や日付にインデックス適用
- **データ前処理**: pandas による効率的なデータ変換処理と一括処理
- **非同期処理**: FastAPI の非同期サポートを活用した高速レスポンス
- **SQLクエリ最適化**: ORM設計での効率的なクエリ実行計画
- **メモリ使用量の最適化**: 大規模CSVファイルの効率的な処理アルゴリズム

### 3. UI/UX設計

- **インタラクティブフィルタ**: リアルタイムフィルタリングでユーザ体験向上
- **レスポンシブ設計**: 様々なデバイスサイズに対応
- **データビジュアライゼーション**: 直感的に理解できるグラフ表現と配色設計
- **ダッシュボードレイアウト**: 情報階層と重要度を考慮した画面設計
- **ユーザーフィードバック**: 処理状況の視覚的フィードバック（プログレスバー、ローディング表示）

### 4. 拡張性と外部連携

- **Google Sheets連携**: GASスクリプトとの連携によるスプレッドシートデータの自動取り込み
- **Webhook対応**: 外部サービスからのデータ更新通知に対応
- **バッチ処理対応**: 定期実行スクリプトによるデータ自動更新
- **外部APIサポート**: 広告プラットフォームAPIとの将来的な連携を考慮した設計

```python
# Google Sheets連携サンプルコード
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests

# 1. Google Sheets認証
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 2. スプレッドシートデータ取得
spreadsheet = client.open("広告KPIデータ")
worksheet = spreadsheet.worksheet("日次レポート")
data = worksheet.get_all_records()

# 3. pandas DataFrameに変換
df = pd.DataFrame(data)

# 4. CSVとして一時保存
temp_csv = "temp_data.csv"
df.to_csv(temp_csv, index=False)

# 5. APIを使ってアップロード
with open(temp_csv, 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/upload', files=files)
    
print(f"アップロード結果: {response.status_code} - {response.text}")

# 6. Excelレポート連携例
# CTRとCVRの数式を動的に生成
ctr_formulas = []
kpi_formulas = []
for i in range(len(df)):
    row_num = i + 2  # Excelは1始まり、ヘッダー行があるため+2
    ctr_formula = f'=IFERROR(D{row_num}/C{row_num}*100, "")'
    kpi_formula = f'=IFERROR(F{row_num}/C{row_num}*1000, "")'
    ctr_formulas.append(ctr_formula)
    kpi_formulas.append(kpi_formula)

# 新しいカラムに追加
df["ctr"] = ctr_formulas
df["kpi"] = kpi_formulas
```

### 5. エラーハンドリングとデータ品質管理

- **包括的な例外処理**: 各層で適切な例外捕捉と処理
- **ログ記録**: 日付ベースのログファイルによる操作追跡（トレーサビリティ）
- **データバリデーション**: 入力データの検証と適切なフィードバック
- **型安全性確保**: 一貫したデータ型の強制とチェック
- **自動リカバリー**: データ取り込み失敗時の自動復旧メカニズム

### 6. コード品質と開発プラクティス

- **モジュール分割**: 単一責任の原則に基づいた機能分割
- **型ヒント**: Pythonの型アノテーションを活用した可読性と安全性向上
- **ドキュメンテーション**: 関数とクラスの詳細なドキュメント（docstring）
- **一貫したコーディングスタイル**: PEP8準拠のコードフォーマット
- **テスト可能な設計**: 各コンポーネントの単体テスト対応

## 📋 画面イメージとUI機能

### メインダッシュボード
![メインダッシュボード](https://i.imgur.com/5BdjHBU.png)

メインダッシュボードでは以下の機能を提供します：
- 全体KPI概要（インプレッション、クリック、コンバージョン、コスト）
- 期間指定フィルター
- キャンペーン選択
- リアルタイムデータ更新

### KPI推移グラフ
![KPI推移グラフ](https://i.imgur.com/JpFxLsm.png)

KPI推移グラフでは以下を表示：
- CPA（獲得単価）推移
- CVR（コンバージョン率）推移
- CTR（クリック率）推移
- タブ切り替えによる表示切替

### キャンペーン比較
![キャンペーン比較](https://i.imgur.com/K9f3mTY.png)

キャンペーン比較では以下の分析が可能：
- 複数キャンペーンのCPA/CVR/CTR比較
- バーチャートによる視覚的比較
- コスト配分の分析
- パフォーマンス順位付け

### データテーブル＆エクスポート
![データテーブル](https://i.imgur.com/L8dGvsa.png)

データテーブル機能：
- 生データの表示と検索
- ソート機能
- CSV/Excelエクスポート
- ページネーション

## 🚀 セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/advertisement-kpi-streamfast-db.git
cd advertisement-kpi-streamfast-db
```

### 2. 仮想環境のセットアップ

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. アプリケーションの実行

```bash
# Windows
scripts\run.bat

# Mac/Linux
chmod +x scripts/run.sh
./scripts/run.sh
```

### 5. アプリケーションへのアクセス

- **Streamlit UI**: http://localhost:8501
- **FastAPI ドキュメント**: http://localhost:8000/docs

## 📁 プロジェクト構成

```
advertisement-kpi-streamfast-db/
├── backend/              # バックエンドAPI (FastAPI)
│   ├── __init__.py
│   ├── main.py           # APIエンドポイント
│   ├── models.py         # データモデル定義
│   ├── db_init.py        # DB初期化スクリプト
│   └── utils.py          # ユーティリティ関数
│
├── frontend/             # フロントエンド (Streamlit)
│   ├── __init__.py
│   ├── dashboard.py      # メインダッシュボード
│   ├── components.py     # UIコンポーネント
│   └── config.py         # 設定ファイル
│
├── data/                 # データファイル
│   └── sample_kpi.csv    # サンプルCSV
│
├── log/                  # ログファイル (自動生成)
│
├── scripts/              # 実行スクリプト
│   ├── run.bat           # Windows用起動スクリプト
│   └── run.sh            # Mac/Linux用起動スクリプト
│
├── requirements.txt      # 依存パッケージリスト
├── setup.py              # パッケージ設定
├── LICENSE               # MIT ライセンス
└── README.md             # プロジェクト説明
```

## 📈 技術選定理由と設計思想

本プロジェクトでは、実務での広告効果測定業務の効率化という明確な目的に基づいて技術選定を行いました。

### Streamlit + FastAPI の組み合わせ
Streamlitはデータサイエンティストやビジネスアナリストでも扱いやすいUIを提供し、FastAPIは高速で型安全なバックエンドを実現。この組み合わせにより、フロントエンド開発の工数を大幅に削減しながらも、拡張性の高いAPIを実現しています。従来のフルスタックウェブフレームワークと比較して、開発速度が3倍以上向上しています。

### SQLite + SQLAlchemy の採用
小〜中規模のデータセットに対して最適な組み合わせとして選定。SQLiteの軽量さとファイルベースの特性により、デプロイやバックアップが容易になり、SQLAlchemyによるORM層の実装で将来的なDB移行の負担を軽減しています。特に、インメモリデータベースからファイルベースへのシームレスな移行を可能にし、スケーラビリティを確保しています。

### モジュラーアーキテクチャ
各コンポーネントが疎結合になるよう設計し、将来的な機能拡張や技術入れ替えに対応。特に、バックエンドとフロントエンドの分離により、UIの変更がデータ層に影響を与えない構造としています。これにより、チーム開発時の並行作業が可能になり、開発効率が向上します。

### 実務主導設計
広告代理店や企業のマーケティング部門での実務を詳細に分析し、日常的なKPI分析ワークフローを効率化。特に、キャンペーン別比較や時系列分析など、意思決定に必要な情報を即座に提供できる構成としています。ユーザーの実際の業務フローに合わせたUIレイアウトとショートカットを実装し、学習コストを最小化しています。

## 📊 主な機能と使い方

### 1. CSVデータのインポート
- サイドバーの「CSVファイルを選択」からファイルをアップロード
- 「追加」または「置換」モードを選択してデータベースに登録
- サンプルデータ生成機能によるデモデータの作成も可能

### 2. データフィルタリングとKPI分析
- キャンペーンおよび日付範囲による絞り込み
- リアルタイムでのデータ更新とグラフ再描画
- 主要KPI指標（CPA、CVR、CTR）の時系列分析

### 3. キャンペーン比較と最適化
- 複数キャンペーンの横断比較
- ROI（投資対効果）分析
- キャンペーンパフォーマンスのランキング

### 4. データエクスポートとレポート作成
- CSV/Excel形式でのデータエクスポート
- カスタムフィルタリング条件の保存
- 定期レポート作成の自動化対応

### 5. API連携と外部システム統合
- RESTful APIによる外部システムとの連携
- Webhookによる自動データ更新
- Google Sheets、Excelとの双方向データ連携

## 🔄 Git管理とバージョン管理戦略

本プロジェクトではGitFlow戦略を採用し、効率的な開発とリリース管理を実現しています。

### ブランチ構造
- `main`: 安定版コード（本番リリース）
- `develop`: 開発中のコード（次期リリース候補）
- `feature/*`: 新機能開発用ブランチ
- `bugfix/*`: バグ修正用ブランチ
- `release/*`: リリース準備用ブランチ

### コミット規約
セマンティックコミットメッセージを採用し、コードの変更内容を明確に伝えます：
- `feat:` 新機能の追加
- `fix:` バグ修正
- `docs:` ドキュメント更新
- `style:` コードスタイル変更
- `refactor:` リファクタリング
- `perf:` パフォーマンス改善
- `test:` テストコード追加・修正

### 開発フロー
1. 機能追加やバグ修正は `feature/` または `bugfix/` ブランチで実施
2. プルリクエストを通して `develop` ブランチにマージ
3. リリース準備ができたら `release/` ブランチを作成
4. テスト後、`main` にマージしてリリース
5. `main` から `develop` にマージバックして同期維持

## 📈 今後の展望と拡張計画

### 1. データソース拡張
- Google Ads、Facebook、Twitter等の広告APIからの直接データ取得
- CSVインポート処理の自動化と定期実行

### 2. 分析機能強化
- 機械学習モデルによる広告パフォーマンス予測
- 異常検知によるパフォーマンス低下の早期発見
- コホート分析とLTV（顧客生涯価値）計算

### 3. UI/UX改善
- ダークモード対応
- モバイル最適化
- ユーザーカスタマイズ可能なダッシュボード

### 4. 認証・権限管理
- ユーザー認証システム
- ロールベースのアクセス制御
- データ閲覧/編集権限の管理
