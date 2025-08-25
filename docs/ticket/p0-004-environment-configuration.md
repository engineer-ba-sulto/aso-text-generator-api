### チケット: P0-004 環境設定

#### 背景 / 目的

- **背景**: プロジェクト構造は整備済みだが、Google AI (Gemini) APIキーなどの環境変数管理が未整備
- **目的**: `.env`ファイルでGoogle AI (Gemini) APIキーを管理し、環境変数の設定を行って、セキュアな設定管理を確立する

#### スコープ（このチケットでやること）

- **環境変数ファイルの作成**
  ```bash
  # .env.example
  # Google AI (Gemini) API設定
  GOOGLE_API_KEY=your_google_api_key_here
  
  # アプリケーション設定
  APP_NAME=ASO Text Generator API
  APP_VERSION=1.0.0
  DEBUG=False
  
  # サーバー設定
  HOST=0.0.0.0
  PORT=8000
  
  # ログ設定
  LOG_LEVEL=INFO
  
  # ファイルアップロード設定
  MAX_FILE_SIZE=10485760  # 10MB
  ALLOWED_EXTENSIONS=.csv
  ```

- **設定管理クラスの実装**
  ```python
  # app/config.py
  from pydantic_settings import BaseSettings
  from typing import Optional
  
  class Settings(BaseSettings):
      # Google AI設定
      google_api_key: str
      
      # アプリケーション設定
      app_name: str = "ASO Text Generator API"
      app_version: str = "1.0.0"
      debug: bool = False
      
      # サーバー設定
      host: str = "0.0.0.0"
      port: int = 8000
      
      # ログ設定
      log_level: str = "INFO"
      
      # ファイルアップロード設定
      max_file_size: int = 10485760
      allowed_extensions: str = ".csv"
      
      class Config:
          env_file = ".env"
          env_file_encoding = "utf-8"
  ```

- **セキュリティ設定**
  - `.env`ファイルを`.gitignore`に追加
  - APIキーの暗号化・復号化機能（オプション）
  - 環境変数のバリデーション

#### やらないこと（Out of Scope）

- エラーハンドリングの実装（P0-005で対応）
- 各サービスクラスの実装（STEP1以降で対応）
- 実際のAPIキーの設定（開発者が手動で実行）

#### 受入条件（Acceptance Criteria）

- `.env.example`ファイルが作成され、必要な環境変数が定義されていること
- `app/config.py`で設定管理クラスが実装されていること
- 環境変数が適切にバリデーションされていること
- `.env`ファイルが`.gitignore`に追加されていること
- アプリケーションが環境変数を正常に読み込めること

#### 影響/変更ファイル

- 追加:
  - `.env.example`
- 変更:
  - `app/config.py`（設定管理クラスの実装）
  - `.gitignore`（.envファイルの追加）

#### 依存関係 / ブロッカー

- P0-001（プロジェクト初期化）の完了が必要
- P0-002（依存関係管理）の完了が必要
- P0-003（プロジェクト構造）の完了が必要
- ただし、P0-005（エラーハンドリング）は本チケットの完了に依存

#### 参考資料

- `docs/MVP開発ロードマップ.md` の「ステップ0：プロジェクト基盤の構築」
- [Python-dotenv公式ドキュメント](https://github.com/theskumar/python-dotenv)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [環境変数管理ベストプラクティス](https://12factor.net/config)

#### リスク / 留意点

- 機密情報（APIキー）の適切な管理
- 環境別の設定ファイル管理（開発・本番）
- 設定値の型安全性を保証
- デフォルト値の適切な設定

#### 見積り

- 1時間（計画準拠）
