### チケット: P0-001 プロジェクト初期化

#### 背景 / 目的

- **背景**: 新規プロジェクトのため、Python 仮想環境と FastAPI プロジェクトの基本構造が存在しない状態
- **目的**: Python 仮想環境を作成し、FastAPI プロジェクトの基本構造を構築して、以降の開発の基盤を整備する

#### スコープ（このチケットでやること）

- **Python 仮想環境の作成**

  - `python -m venv venv` で仮想環境を作成
  - 仮想環境のアクティベートスクリプトを準備

- **FastAPI プロジェクトの基本構造構築**

  ```
  api/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config.py
  │   ├── services/
  │   │   └── __init__.py
  │   └── api/
  │       ├── __init__.py
  │       └── v1/
  │           └── __init__.py
  ├── requirements.txt
  ├── .env.example
  ├── .gitignore
  └── README.md
  ```

- **基本ファイルの作成**
  - `app/main.py`: FastAPI アプリケーションのエントリーポイント
  - `app/config.py`: 設定管理クラス
  - `requirements.txt`: 依存関係リスト
  - `.env.example`: 環境変数テンプレート
  - `.gitignore`: Git 除外設定

#### やらないこと（Out of Scope）

- 依存関係の詳細定義（P0-002 で対応）
- プロジェクト構造の詳細設計（P0-003 で対応）
- 環境変数の詳細設定（P0-004 で対応）
- エラーハンドリングの実装（P0-005 で対応）

#### 受入条件（Acceptance Criteria）

- Python 仮想環境が正常に作成され、アクティベートできること
- FastAPI アプリケーションが起動し、ヘルスチェックエンドポイントが動作すること
- プロジェクト構造が上記のディレクトリ構成に従っていること
- 基本的な設定ファイルが適切に配置されていること

#### 影響/変更ファイル

- 追加:
  - `app/__init__.py`
  - `app/main.py`
  - `app/config.py`
  - `app/services/__init__.py`
  - `app/api/__init__.py`
  - `app/api/v1/__init__.py`
  - `requirements.txt`
  - `.env.example`
  - `.gitignore`
  - `README.md`
- 作成: `venv/` ディレクトリ

#### 依存関係 / ブロッカー

- なし（単独で作成可能）
- ただし、P0-002（依存関係管理）は本チケットの完了に依存

#### 参考資料

- `docs/MVP開発ロードマップ.md` の「ステップ 0：プロジェクト基盤の構築」
- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [Python 仮想環境ガイド](https://docs.python.org/3/tutorial/venv.html)

#### リスク / 留意点

- Python 3.8 以上が必要
- FastAPI の最新安定版を使用する
- 仮想環境名は`venv`とする
- プロジェクト構造は拡張性を考慮した設計とする

#### 見積り

- 2 時間（計画準拠）
