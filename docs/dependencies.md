# 依存関係管理

## 概要

このドキュメントでは、ASO Text Generator API プロジェクトで使用する Python パッケージの依存関係について説明します。

## パッケージ一覧（requirements.txt）

### Web Framework & Server

- **fastapi>=0.104.0**: モダンな Web フレームワーク

  - 高速な API 開発
  - 自動ドキュメント生成
  - 型ヒントによるバリデーション

- **uvicorn[standard]>=0.24.0**: ASGI サーバー
  - FastAPI アプリケーションの実行
  - 高パフォーマンスな HTTP サーバー

### データ処理

- **pandas>=2.0.0**: データ分析・処理ライブラリ
  - CSV ファイルの読み込み・処理
  - データの分析・変換

### ファイル処理

- **python-multipart>=0.0.6**: マルチパートデータ処理
  - ファイルアップロード機能
  - フォームデータの処理

### AI・機械学習

- **google-genai>=0.1.0**: Google Generative AI SDK
  - Gemini API との連携
  - テキスト生成機能

### 環境・設定管理

- **python-dotenv>=1.0.0**: 環境変数管理

  - .env ファイルからの環境変数読み込み
  - 設定の外部化

- **pydantic>=2.0.0**: データバリデーション
  - リクエスト・レスポンスの型チェック
  - データの自動変換

### HTTP 通信

- **httpx>=0.24.0**: HTTP クライアント
  - 外部 API との通信
  - 非同期 HTTP リクエスト

### ログ管理

- **loguru>=0.7.0**: ログライブラリ
  - 構造化ログ
  - カラー出力・ローテーション

## 開発用パッケージ

### テスト

- **pytest>=7.4.0**: テストフレームワーク
- **pytest-asyncio>=0.21.0**: 非同期テストサポート
- **pytest-cov>=4.1.0**: カバレッジ測定

### コード品質

- **black>=23.0.0**: コードフォーマッター
- **isort>=5.12.0**: インポート文の整理
- **flake8>=6.0.0**: リンター
- **mypy>=1.5.0**: 型チェッカー

### 開発ツール

- **pre-commit>=3.0.0**: Git フック管理
- **jupyter>=1.0.0**: Jupyter Notebook
- **ipython>=8.0.0**: 対話的 Python シェル

### ドキュメント

- **mkdocs>=1.5.0**: ドキュメント生成
- **mkdocs-material>=9.0.0**: Material for MkDocs テーマ

## インストール方法

```bash
# すべての依存関係をインストール
pip install -r requirements.txt
```

## バージョン管理方針

- 最小バージョンを`>=`で指定
- セキュリティアップデートを考慮
- 互換性を保ちながら最新版を使用

## 依存関係の更新

定期的に依存関係を更新し、セキュリティパッチを適用してください：

```bash
# 依存関係の確認
pip list --outdated

# 特定パッケージの更新
pip install --upgrade package-name

# requirements.txtの更新
pip freeze > requirements.txt
```
