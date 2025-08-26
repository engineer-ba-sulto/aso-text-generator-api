# ASO Text Generator API

ASO（App Store Optimization）最適化のためのテキスト生成 API

## 📋 概要

この API は、アプリストアでの検索最適化（ASO）を支援するためのテキスト生成サービスです。アプリの説明文、キーワード、タイトルなどの最適化されたテキストを自動生成します。

### 🎯 主な機能

- **CSV 分析**: キーワード調査 CSV ファイルの自動分析
- **キーワード選定**: 統計分析による主要キーワードの自動選定
- **テキスト生成**: Gemini AI を使用した多言語テキスト生成
- **ASO 最適化**: 戦略ルールに基づいた最適化されたテキスト生成

## 🚀 機能詳細

### 統合 API エンドポイント

- **`POST /api/v1/generate-aso-texts`**: 全テキスト項目を一括生成
- **`POST /api/v1/generate-keyword-field`**: キーワードフィールド（100 文字）生成
- **`POST /api/v1/generate-title`**: タイトル（30 文字）生成
- **`POST /api/v1/generate-subtitle`**: サブタイトル（30 文字）生成
- **`POST /api/v1/generate-description`**: 説明文（4000 文字）生成
- **`POST /api/v1/generate-whats-new`**: 最新情報（4000 文字）生成

### 個別 API エンドポイント

- **`POST /api/v1/analyze-csv`**: CSV ファイル分析
- **`POST /api/v1/select-keywords`**: キーワード選定
- **`POST /api/v1/optimized/generate-aso-texts`**: 最適化された統合生成

### モデル情報エンドポイント

- **`GET /api/v1/models`**: 利用可能な Gemini モデルの一覧を取得

## 🛠️ 技術スタック

### バックエンド

- **Framework**: FastAPI 0.104.0+
- **Python**: 3.8+
- **ASGI Server**: Uvicorn 0.24.0+
- **Validation**: Pydantic 2.0.0+
- **Environment**: python-dotenv 1.0.0+

### AI・データ処理

- **AI Model**: Google Gemini (google-genai 0.1.0+)
- **Data Processing**: Pandas 2.0.0+
- **HTTP Client**: httpx 0.24.0+

### 開発・テスト

- **Testing**: pytest 7.4.0+, pytest-asyncio 0.21.0+, pytest-cov 4.1.0+
- **Code Quality**: black 23.0.0+, isort 5.12.0+, flake8 6.0.0+, mypy 1.5.0+
- **Development**: pre-commit 3.0.0+, jupyter 1.0.0+
- **Documentation**: mkdocs 1.5.0+, mkdocs-material 9.0.0+

### システム監視

- **Monitoring**: psutil 5.9.0+
- **Logging**: loguru 0.7.0+

## 📦 インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd aso-text-generator-api
```

### 2. 仮想環境の作成とアクティベート

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境のアクティベート
# macOS/Linux
# bash
source venv/bin/activate
# fish
source venv/bin/activate.fish
# Windows
venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
# すべての依存関係をインストール（本番・開発用含む）
pip install -r requirements.txt
```

### 4. 環境変数の設定

```bash
# 環境変数テンプレートをコピー
cp env.example .env

# .envファイルを編集して必要な設定を行う
# 特にGOOGLE_API_KEYとGEMINI_API_KEYを設定してください
```

### 5. Gemini モデルの設定（オプション）

```bash
# .envファイルでGeminiモデルを指定
GEMINI_MODEL=gemini-2.5-flash  # デフォルト（推奨）
# または
GEMINI_MODEL=gemini-2.5-pro    # 高精度モデル
# または
GEMINI_MODEL=gemini-2.0-flash  # 高速モデル
```

### 6. 環境変数の設定例

`.env`ファイルの設定例：

```bash
# Google AI API設定
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Geminiモデル設定
GEMINI_MODEL=gemini-model

# Gemini API設定
GEMINI_TIMEOUT=30
GEMINI_MAX_RETRIES=3

# アプリケーション設定
DEBUG=false
LOG_LEVEL=INFO

# サーバー設定
HOST=0.0.0.0
PORT=8000
```

#### 必要な環境変数

```bash
# Google AI API設定
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# アプリケーション設定
APP_NAME="ASO Text Generator API"
APP_VERSION="1.0.0"
DEBUG=false

# サーバー設定
HOST="0.0.0.0"
PORT=8000

# ログ設定
LOG_LEVEL="INFO"

# ファイルアップロード設定
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=".csv"
```

## 🏃‍♂️ 実行

### 開発サーバーの起動

```bash
# 直接実行
python3 -m app.main

# または uvicorn を使用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### アクセス

- **API**: http://localhost:8000
- **ドキュメント**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **ヘルスチェック**: http://localhost:8000/health

## 📁 プロジェクト構造

```
aso-text-generator-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPIアプリケーションのエントリーポイント
│   ├── config.py                  # 設定管理
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── aso_endpoints.py   # メインAPIエンドポイント
│   │       └── optimized_aso_endpoints.py  # 最適化版エンドポイント
│   ├── models/
│   │   ├── __init__.py
│   │   ├── csv_models.py          # CSV関連モデル
│   │   ├── error_models.py        # エラーモデル
│   │   ├── request_models.py      # リクエストモデル
│   │   └── response_models.py     # レスポンスモデル
│   ├── services/
│   │   ├── __init__.py
│   │   ├── aso_text_orchestrator.py      # 統合テキスト生成オーケストレーター
│   │   ├── csv_analyzer.py               # CSV分析サービス
│   │   ├── csv_validator.py              # CSV検証サービス
│   │   ├── description_generator.py      # 説明文生成サービス
│   │   ├── gemini_generator.py           # Gemini AI統合サービス
│   │   ├── individual_text_orchestrator.py  # 個別テキスト生成オーケストレーター
│   │   ├── keyword_field_generator.py    # キーワードフィールド生成サービス
│   │   ├── keyword_scorer.py             # キーワードスコアリングサービス
│   │   ├── keyword_selector.py           # キーワード選定サービス
│   │   ├── optimized_individual_orchestrator.py  # 最適化版個別オーケストレーター
│   │   ├── subtitle_generator.py         # サブタイトル生成サービス
│   │   ├── text_generator.py             # 基本テキスト生成サービス
│   │   ├── title_generator.py            # タイトル生成サービス
│   │   ├── whats_new_generator.py        # 最新情報生成サービス
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── en.py                     # 英語プロンプト
│   │       └── ja.py                     # 日本語プロンプト
│   └── utils/
│       ├── __init__.py
│       ├── cache_manager.py              # キャッシュ管理
│       ├── error_handler.py              # エラーハンドリング
│       ├── exceptions.py                 # カスタム例外
│       ├── flow_logger.py                # フローログ
│       ├── language_validator.py         # 言語検証
│       ├── resource_manager.py           # リソース管理
│       └── response_builder.py           # レスポンス構築
├── docs/
│   ├── api_spec.md                      # API仕様書
│   ├── ASO戦略ルールまとめ.md            # ASO戦略ルール
│   ├── dependencies.md                   # 依存関係ドキュメント
│   ├── MVP開発ロードマップ.md            # MVP開発ロードマップ
│   ├── PRD.md                           # 製品要求仕様書
│   ├── 実装計画書.md                     # 実装計画書
│   └── ticket/                          # 開発チケット
├── tests/
│   ├── __init__.py
│   ├── test_csv_analyzer.py             # CSV分析テスト
│   ├── test_csv_validator.py            # CSV検証テスト
│   ├── test_description_generator.py    # 説明文生成テスト
│   ├── test_gemini_generator.py         # Gemini生成テスト
│   ├── test_keyword_field_generator.py  # キーワードフィールド生成テスト
│   ├── test_keyword_scorer.py           # キーワードスコアリングテスト
│   ├── test_keyword_selector.py         # キーワード選定テスト
│   ├── test_prompts.py                  # プロンプトテスト
│   ├── test_response_builder.py         # レスポンス構築テスト
│   ├── test_subtitle_generator.py       # サブタイトル生成テスト
│   ├── test_text_generator.py           # テキスト生成テスト
│   ├── test_title_generator.py          # タイトル生成テスト
│   └── test_whats_new_generator.py      # 最新情報生成テスト
├── requirements.txt                     # 依存関係
├── .gitignore                          # Git除外設定
├── .coverage                           # テストカバレッジ
├── README.md                           # このファイル
└── venv/                               # 仮想環境
```

## 🔧 開発

### コードフォーマット

```bash
# Black によるコードフォーマット
black .

# isort によるインポート整理
isort .

# flake8 によるリント
flake8 .

# mypy による型チェック
mypy .
```

### テスト

```bash
# テストの実行
pytest

# カバレッジ付きテスト
pytest --cov=app

# 特定のテストファイル実行
pytest tests/test_csv_analyzer.py

# テストレポート生成
pytest --cov=app --cov-report=html
```

### 開発ツール

```bash
# pre-commitフックのインストール
pre-commit install

# Jupyter notebook起動
jupyter notebook

# IPython起動
ipython
```

## 📝 API ドキュメント

### モデル選択機能

#### 利用可能なモデルの確認

```http
GET /api/v1/models
```

**レスポンス例:**

```json
{
  "recommended_models": ["gemini-2.5-flash", "gemini-2.5-pro"],
  "acceptable_models": ["gemini-2.0-flash", "gemini-2.0-pro"],
  "current_default": "gemini-2.5-flash",
  "model_categories": {
    "recommended": "最新の推奨モデル（最高性能）",
    "acceptable": "許容モデル（明示的に要求された場合のみ使用）",
    "deprecated": "非推奨モデル（使用禁止）"
  }
}
```

#### リクエストでのモデル指定

```json
{
  "csv_file": "file",
  "app_name": "string",
  "features": ["string"],
  "language": "ja",
  "model_name": "gemini-2.5-pro" // オプション：使用するモデルを指定
}
```

### 主要エンドポイント

#### 統合テキスト生成

```http
POST /api/v1/generate-aso-texts
Content-Type: multipart/form-data

{
  "csv_file": "file",
  "app_name": "string",
  "features": ["string"],
  "language": "ja|en"
}
```

#### 個別テキスト生成

```http
POST /api/v1/generate-keyword-field
POST /api/v1/generate-title
POST /api/v1/generate-subtitle
POST /api/v1/generate-description
POST /api/v1/generate-whats-new
```

### レスポンス形式

```json
{
  "success": true,
  "data": {
    "keyword_field": "主要キーワード 関連キーワード1 関連キーワード2",
    "title": "主要キーワード - アプリ名",
    "subtitle": "アプリの価値を伝えるサブタイトル",
    "description": "詳細なアプリ説明文...",
    "whats_new": "最新情報の説明文..."
  },
  "language": "ja",
  "metadata": {
    "generated_at": "2024-01-01T00:00:00Z",
    "processing_time": 2.5
  }
}
```

詳細な API 仕様は以下の URL で確認できます：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 デプロイ

### 本番環境での実行

```bash
# 本番用サーバー起動
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# または gunicorn を使用
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker 化（推奨）

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 パフォーマンス

- **レスポンス時間**: 平均 2-5 秒（Gemini API 呼び出し含む）
- **同時接続**: 最大 100 リクエスト/分
- **ファイルサイズ制限**: 10MB（CSV ファイル）
- **メモリ使用量**: 約 200-500MB

## 🔒 セキュリティ

- **API 認証**: 現在は不要（MVP 段階）
- **入力検証**: Pydantic による厳密なバリデーション
- **ファイル検証**: CSV ファイル形式とサイズ制限
- **エラーハンドリング**: 詳細なエラーレスポンス
- **ログ管理**: セキュアなログ出力

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### 開発ガイドライン

- コードは PEP 8 に準拠
- 新機能にはテストを追加
- ドキュメントを更新
- pre-commit フックを使用

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 📞 サポート

### 問題の報告

質問や問題がある場合は、以下の方法でサポートを受けることができます：

1. **GitHub Issues**: バグ報告や機能要求
2. **ドキュメント**: `/docs` フォルダ内の詳細ドキュメント
3. **API 仕様**: `/docs` エンドポイントでの Swagger UI

### よくある質問

**Q: CSV ファイルの形式は？**
A: キーワード、ランキング、人気度、難易度の列を含む CSV ファイルが必要です。

**Q: 対応言語は？**
A: 日本語（ja）と英語（en）に対応しています。

**Q: API キーは必要ですか？**
A: はい、Google Gemini API キーが必要です。

**Q: 生成されるテキストの品質は？**
A: ASO 戦略ルールに基づいて最適化された高品質なテキストを生成します。
