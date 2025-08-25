### チケット: P0-003 プロジェクト構造

#### 背景 / 目的

- **背景**: 基本構造は作成済みだが、多言語対応を前提とした詳細なプロジェクト構造が未整備
- **目的**: 多言語対応を前提としたプロジェクト構造を構築し、`app/services/prompts`ディレクトリを作成して、拡張可能なアーキテクチャを確立する

#### スコープ（このチケットでやること）

- **多言語対応ディレクトリ構造の作成**
  ```
  api/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config.py
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── csv_analyzer.py
  │   │   ├── keyword_selector.py
  │   │   ├── text_generator.py
  │   │   ├── gemini_generator.py
  │   │   └── prompts/
  │   │       ├── __init__.py
  │   │       ├── ja.py
  │   │       └── en.py
  │   ├── api/
  │   │   ├── __init__.py
  │   │   └── v1/
  │   │       ├── __init__.py
  │   │       └── aso_endpoints.py
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── request_models.py
  │   │   └── response_models.py
  │   └── utils/
  │       ├── __init__.py
  │       └── error_handler.py
  ├── tests/
  │   ├── __init__.py
  │   ├── test_csv_analyzer.py
  │   ├── test_keyword_selector.py
  │   └── test_text_generator.py
  └── docs/
      └── api_spec.md
  ```

- **多言語プロンプト管理構造**
  - `app/services/prompts/ja.py`: 日本語プロンプト定義
  - `app/services/prompts/en.py`: 英語プロンプト定義
  - 各言語ファイルに共通のプロンプト構造を定義

- **サービス層の設計**
  - `csv_analyzer.py`: CSV分析サービス
  - `keyword_selector.py`: キーワード選定サービス
  - `text_generator.py`: テキスト生成サービス
  - `gemini_generator.py`: Gemini API連携サービス

#### やらないこと（Out of Scope）

- 各サービスクラスの実装（STEP1以降で対応）
- 環境変数の詳細設定（P0-004で対応）
- エラーハンドリングの実装（P0-005で対応）
- テストコードの実装（各ステップで対応）

#### 受入条件（Acceptance Criteria）

- 上記のディレクトリ構造が正確に作成されていること
- 各ディレクトリに`__init__.py`ファイルが配置されていること
- 多言語プロンプトディレクトリ（`prompts/`）が作成されていること
- サービス層の基本クラス構造が定義されていること
- テストディレクトリが適切に配置されていること

#### 影響/変更ファイル

- 追加:
  - `app/services/csv_analyzer.py`
  - `app/services/keyword_selector.py`
  - `app/services/text_generator.py`
  - `app/services/gemini_generator.py`
  - `app/services/prompts/__init__.py`
  - `app/services/prompts/ja.py`
  - `app/services/prompts/en.py`
  - `app/api/v1/aso_endpoints.py`
  - `app/models/__init__.py`
  - `app/models/request_models.py`
  - `app/models/response_models.py`
  - `app/utils/__init__.py`
  - `app/utils/error_handler.py`
  - `tests/__init__.py`
  - `tests/test_csv_analyzer.py`
  - `tests/test_keyword_selector.py`
  - `tests/test_text_generator.py`
  - `docs/api_spec.md`

#### 依存関係 / ブロッカー

- P0-001（プロジェクト初期化）の完了が必要
- P0-002（依存関係管理）の完了が必要
- ただし、P0-004（環境設定）は本チケットの完了に依存

#### 参考資料

- `docs/MVP開発ロードマップ.md` の「ステップ0：プロジェクト基盤の構築」
- [Pythonプロジェクト構造ガイド](https://docs.python-guide.org/writing/structure/)
- [FastAPIプロジェクト構造](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

#### リスク / 留意点

- モジュール化された設計で拡張性を確保
- 多言語対応を前提とした構造設計
- テスト可能な構造を考慮
- 依存関係の方向性を明確化（API → Services → Models）

#### 見積り

- 1.5時間（計画準拠）
