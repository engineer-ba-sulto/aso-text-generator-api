# ASO Text Generator API

ASO（App Store Optimization）最適化のためのテキスト生成 API

## 📋 概要

この API は、アプリストアでの検索最適化（ASO）を支援するためのテキスト生成サービスです。アプリの説明文、キーワード、タイトルなどの最適化されたテキストを自動生成します。

## 🚀 機能

- アプリ説明文の生成（Gemini AI 使用）
- キーワード最適化
- タイトル生成
- 多言語対応（日本語・英語）

## 🛠️ 技術スタック

- **Framework**: FastAPI
- **Python**: 3.8+
- **ASGI Server**: Uvicorn
- **Validation**: Pydantic
- **Environment**: python-dotenv
- **AI Model**: Google Gemini (GenAI SDK)

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
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

```bash
# 環境変数テンプレートをコピー
cp env.example .env

# .envファイルを編集して必要な設定を行う
# 特にGOOGLE_API_KEYを設定してください
```

## 🏃‍♂️ 実行

### 開発サーバーの起動

```bash
# 直接実行
python -m app.main

# または uvicorn を使用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### アクセス

- **API**: http://localhost:8000
- **ドキュメント**: http://localhost:8000/docs
- **ヘルスチェック**: http://localhost:8000/health

## 📁 プロジェクト構造

```
aso-text-generator-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPIアプリケーションのエントリーポイント
│   ├── config.py        # 設定管理
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       └── __init__.py
│   └── services/
│       └── __init__.py
├── requirements.txt     # 依存関係
├── env.example         # 環境変数テンプレート
├── .gitignore          # Git除外設定
└── README.md           # このファイル
```

## 🔧 開発

### コードフォーマット

```bash
# Black によるコードフォーマット
black .

# isort によるインポート整理
isort .
```

### テスト

```bash
# テストの実行
pytest
```

## 📝 API ドキュメント

API ドキュメントは以下の URL で確認できます：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 📞 サポート

質問や問題がある場合は、Issue を作成してください。
