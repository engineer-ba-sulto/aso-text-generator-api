### チケット: P1-001 CSV データモデルとバリデーション

#### 背景 / 目的

- **背景**: CSV ファイルのアップロード機能は存在するが、ASO キーワード分析に特化したデータモデルとバリデーション機能が未実装
- **目的**: Pydantic を使い、アップロードされる CSV の必須カラムとデータ型を定義・検証し、データ品質を保証する

#### スコープ（このチケットでやること）

- **CSV データモデルの定義**

  ```python
  # app/models/csv_models.py
  from pydantic import BaseModel, Field, validator
  from typing import List, Optional
  import pandas as pd

  class KeywordData(BaseModel):
      """個別キーワードデータモデル"""
      keyword: str = Field(..., min_length=1, max_length=100, description="キーワード")
      ranking: int = Field(..., ge=1, le=1000, description="ランキング（1-1000）")
      popularity: float = Field(..., ge=0.0, le=100.0, description="人気度（0-100）")
      difficulty: float = Field(..., ge=0.0, le=100.0, description="難易度（0-100）")

      @validator('keyword')
      def validate_keyword(cls, v):
          if not v.strip():
              raise ValueError('キーワードは空文字列であってはいけません')
          return v.strip()

  class CSVData(BaseModel):
      """CSV ファイル全体のデータモデル"""
      keywords: List[KeywordData] = Field(..., min_items=1, max_items=1000)

      @validator('keywords')
      def validate_unique_keywords(cls, v):
          keywords = [k.keyword.lower() for k in v]
          if len(keywords) != len(set(keywords)):
              raise ValueError('重複するキーワードが存在します')
          return v
  ```

- **CSV ファイル構造検証**

  ```python
  # app/services/csv_validator.py
  class CSVValidator:
      """CSV ファイル検証クラス"""

      REQUIRED_COLUMNS = ['keyword', 'ranking', 'popularity', 'difficulty']
      MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

      def validate_file_structure(self, df: pd.DataFrame) -> bool:
          """CSV ファイルの構造を検証"""
          # 必須カラムの存在チェック
          missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
          if missing_columns:
              raise CSVValidationError(f"必須カラムが不足しています: {missing_columns}")

          # データ型チェック
          if not pd.api.types.is_string_dtype(df['keyword']):
              raise CSVValidationError("keyword カラムは文字列型である必要があります")

          if not pd.api.types.is_numeric_dtype(df['ranking']):
              raise CSVValidationError("ranking カラムは数値型である必要があります")

          return True
  ```

- **データ型と値の範囲チェック**

  ```python
  def validate_data_ranges(self, df: pd.DataFrame) -> bool:
      """データの値範囲を検証"""
      # ランキング範囲チェック（1-1000）
      if not (df['ranking'] >= 1).all() or not (df['ranking'] <= 1000).all():
          raise CSVValidationError("ranking は 1-1000 の範囲である必要があります")

      # 人気度範囲チェック（0-100）
      if not (df['popularity'] >= 0).all() or not (df['popularity'] <= 100).all():
          raise CSVValidationError("popularity は 0-100 の範囲である必要があります")

      # 難易度範囲チェック（0-100）
      if not (df['difficulty'] >= 0).all() or not (df['difficulty'] <= 100).all():
          raise CSVValidationError("difficulty は 0-100 の範囲である必要があります")

      return True
  ```

- **CSV ファイル読み込みと変換**

  ```python
  def load_and_validate_csv(self, file_path: str) -> CSVData:
      """CSV ファイルを読み込み、検証してデータモデルに変換"""
      try:
          df = pd.read_csv(file_path)

          # 構造検証
          self.validate_file_structure(df)

          # 値範囲検証
          self.validate_data_ranges(df)

          # データモデルに変換
          keywords = []
          for _, row in df.iterrows():
              keyword_data = KeywordData(
                  keyword=row['keyword'],
                  ranking=int(row['ranking']),
                  popularity=float(row['popularity']),
                  difficulty=float(row['difficulty'])
              )
              keywords.append(keyword_data)

          return CSVData(keywords=keywords)

      except pd.errors.EmptyDataError:
          raise CSVValidationError("CSV ファイルが空です")
      except pd.errors.ParserError:
          raise CSVValidationError("CSV ファイルの形式が不正です")
  ```

#### やらないこと（Out of Scope）

- キーワードスコアリングの実装（P1-002 で対応）
- 主要キーワード選定の実装（P1-003 で対応）
- ファイルアップロード機能の実装（既存機能を使用）
- データベースへの保存機能

#### 受入条件（Acceptance Criteria）

- CSV ファイルの必須カラム（keyword, ranking, popularity, difficulty）が適切に検証されること
- データ型と値の範囲が正しくチェックされること
- 重複キーワードの検出が動作すること
- 不正な CSV ファイルに対して適切なエラーメッセージが返されること
- 正常な CSV ファイルが Pydantic モデルに正しく変換されること
- 単体テストが実装され、カバレッジが 90%以上であること

#### 影響/変更ファイル

- 追加:
  - `app/models/csv_models.py` (CSV データモデル)
  - `app/services/csv_validator.py` (CSV 検証サービス)
  - `tests/test_csv_validator.py` (CSV 検証テスト)
- 変更:
  - `app/utils/exceptions.py` (CSV 関連例外の追加)
  - `app/services/csv_analyzer.py` (CSV 検証機能の統合)

#### 依存関係 / ブロッカー

- **依存**: ステップ 0（プロジェクト基盤）の完了
- **ブロッカー**: なし
- **後続**: P1-002（キーワードスコアリング）は本チケットの完了に依存

#### 参考資料

- `docs/MVP開発ロードマップ.md` の「1-1. CSV データモデルとバリデーション」
- [Pydantic 公式ドキュメント](https://docs.pydantic.dev/)
- [Pandas 公式ドキュメント](https://pandas.pydata.org/docs/)

#### リスク / 留意点

- **ファイルサイズ**: 大きな CSV ファイルの処理時のメモリ使用量
- **文字エンコーディング**: 日本語キーワードを含む CSV ファイルの文字化け対策
- **パフォーマンス**: 大量データの検証処理時間
- **エラーメッセージ**: ユーザーにとって分かりやすいエラーメッセージの設計

#### 見積り

- 4 時間（計画準拠）
  - CSV データモデル定義: 1.5 時間
  - バリデーション機能実装: 1.5 時間
  - テスト実装: 1 時間
