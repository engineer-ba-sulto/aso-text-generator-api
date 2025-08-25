# 環境変数設定例

このファイルは`.env`ファイルの設定例です。実際の使用時は`.env`ファイルとしてコピーして使用してください。

## 基本的な設定

```bash
# Google AI API設定
# Google AI StudioまたはVertex AIで取得したAPIキーを設定
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Geminiモデル設定
# 推奨モデル: gemini-2.5-flash, gemini-2.5-pro
# 許容モデル: gemini-2.0-flash, gemini-2.0-pro
# 非推奨モデル: gemini-1.5-flash, gemini-1.5-pro, gemini-pro (使用禁止)
GEMINI_MODEL=gemini-2.5-flash

# Gemini API設定
GEMINI_TIMEOUT=30
GEMINI_MAX_RETRIES=3

# アプリケーション設定
APP_NAME=ASO Text Generator API
APP_VERSION=1.0.0
DEBUG=false

# FastAPI設定
PROJECT_NAME=ASO Text Generator API
PROJECT_DESCRIPTION=App Store Optimization用のテキスト生成API
VERSION=1.0.0
API_V1_STR=/api/v1

# サーバー設定
HOST=0.0.0.0
PORT=8000

# CORS設定
ALLOWED_HOSTS=["*"]

# ログ設定
LOG_LEVEL=INFO

# ファイルアップロード設定
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.csv
```

## モデル選択の例

### 推奨モデル（最高性能）

```bash
# 一般テキスト・マルチモーダル（推奨）
GEMINI_MODEL=gemini-2.5-flash

# コーディング・複雑な推論（推奨）
GEMINI_MODEL=gemini-2.5-pro
```

### 許容モデル（明示的に要求された場合のみ使用）

```bash
# 高速処理（許容）
GEMINI_MODEL=gemini-2.0-flash

# 高精度（許容）
GEMINI_MODEL=gemini-2.0-pro
```

### 非推奨モデル（使用禁止）

以下のモデルは使用できません：

```bash
# ❌ 使用禁止
GEMINI_MODEL=gemini-1.5-flash
GEMINI_MODEL=gemini-1.5-flash-latest
GEMINI_MODEL=gemini-1.5-pro
GEMINI_MODEL=gemini-pro
```

## 開発環境での設定

```bash
# 開発環境用
DEBUG=true
LOG_LEVEL=DEBUG
PORT=8000
HOST=127.0.0.1
```

## 本番環境での設定

```bash
# 本番環境用
DEBUG=false
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0
```

## 使用方法

1. このファイルを`.env`としてコピー
2. 実際の API キーを設定
3. 必要に応じてモデルを変更
4. アプリケーションを起動

```bash
cp docs/env_example.md .env
# .envファイルを編集してAPIキーを設定
```
