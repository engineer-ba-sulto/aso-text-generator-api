### チケット: P0-002 依存関係管理

#### 背景 / 目的

- **背景**: プロジェクト初期化後、必要な Python パッケージが定義されていない状態
- **目的**: `requirements.txt`を作成し、必要な Python パッケージを定義・管理して、開発環境の一貫性を保証する

#### スコープ（このチケットでやること）

- **必須パッケージの定義**

  ```txt
  fastapi>=0.104.0
  uvicorn[standard]>=0.24.0
  pandas>=2.0.0
  python-multipart>=0.0.6
  google-generativeai>=0.3.0
  python-dotenv>=1.0.0
  pydantic>=2.0.0
  ```

- **開発用パッケージの定義**

  ```txt
  # 開発・テスト用
  pytest>=7.4.0
  pytest-asyncio>=0.21.0
  black>=23.0.0
  flake8>=6.0.0
  mypy>=1.5.0
  ```

- **依存関係の詳細説明**
  - **fastapi**: Web フレームワーク
  - **uvicorn**: ASGI サーバー
  - **pandas**: CSV データ処理
  - **python-multipart**: ファイルアップロード処理
  - **google-generativeai**: Gemini API 連携
  - **python-dotenv**: 環境変数管理
  - **pydantic**: データバリデーション

#### やらないこと（Out of Scope）

- パッケージのインストール実行（開発者が手動で実行）
- プロジェクト構造の詳細設計（P0-003 で対応）
- 環境変数の詳細設定（P0-004 で対応）
- エラーハンドリングの実装（P0-005 で対応）

#### 受入条件（Acceptance Criteria）

- `requirements.txt`が作成され、必要なパッケージが定義されていること
- `pip install -r requirements.txt`で正常にインストールできること
- 各パッケージのバージョンが適切に指定されていること
- 開発環境とプロダクション環境の依存関係が分離されていること

#### 影響/変更ファイル

- 追加:
  - `requirements.txt`
  - `requirements-dev.txt`（開発用パッケージ）
- 変更: なし

#### 依存関係 / ブロッカー

- P0-001（プロジェクト初期化）の完了が必要
- ただし、P0-003（プロジェクト構造）は本チケットの完了に依存

#### 参考資料

- `docs/MVP開発ロードマップ.md` の「ステップ 0：プロジェクト基盤の構築」
- [FastAPI 依存関係](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [Pandas 公式ドキュメント](https://pandas.pydata.org/docs/)

#### リスク / 留意点

- バージョン指定は`>=`を使用して最小バージョンを保証
- セキュリティアップデートを考慮したバージョン範囲設定
- 開発用パッケージは別ファイル（`requirements-dev.txt`）で管理
- 依存関係の競合がないことを確認

#### 見積り

- 1 時間（計画準拠）
