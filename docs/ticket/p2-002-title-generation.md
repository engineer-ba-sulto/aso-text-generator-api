### チケット: P2-002 タイトル (30 文字) 生成

#### 背景 / 目的

- **背景**: キーワードフィールド生成機能は実装済みだが、主要キーワードとアプリ基本名を組み合わせて 30 文字以内のタイトルを生成する機能が未実装
- **目的**: `「{主要キーワード} - {アプリ基本名}」` のテンプレートに基づき、30 文字制限内で最適化されたアプリタイトルを生成する

#### スコープ（このチケットでやること）

- **タイトル生成アルゴリズムの実装**

  ```python
  # app/services/title_generator.py
  from typing import List, Dict, Any, Optional
  from app.utils.exceptions import TextGenerationError
  import re
  import logging

  logger = logging.getLogger(__name__)

  class TitleGenerator:
      """タイトル生成クラス"""

      def __init__(self):
          self.max_length = 30  # 最大文字数
          self.separator = " - "  # 区切り文字
          self.min_app_name_length = 3  # 最小アプリ名長
          self.max_app_name_length = 15  # 最大アプリ名長

      def generate_title(
          self,
          primary_keyword: str,
          app_base_name: str,
          language: str = "ja"
      ) -> str:
          """
          タイトルを生成

          Args:
              primary_keyword: 主要キーワード
              app_base_name: アプリ基本名
              language: 言語（"ja" or "en"）

          Returns:
              生成されたタイトル
          """
          try:
              # 入力データの検証
              self._validate_inputs(primary_keyword, app_base_name)

              # 主要キーワードを処理
              processed_keyword = self._process_primary_keyword(primary_keyword, language)

              # アプリ基本名を処理
              processed_app_name = self._process_app_name(app_base_name, language)

              # 区切り文字を取得
              separator = self._get_separator(language)

              # タイトルを構築
              title = self._build_title(processed_keyword, separator, processed_app_name)

              # 最終検証
              self._validate_title(title)

              logger.info(f"タイトルを生成しました: {title}")

              return title

          except Exception as e:
              logger.error(f"タイトル生成中にエラーが発生しました: {str(e)}")
              raise TextGenerationError(f"タイトル生成に失敗しました: {str(e)}")

      def _validate_inputs(self, primary_keyword: str, app_base_name: str) -> bool:
          """入力データを検証"""
          if not primary_keyword or not primary_keyword.strip():
              raise TextGenerationError("主要キーワードが空です")

          if not app_base_name or not app_base_name.strip():
              raise TextGenerationError("アプリ基本名が空です")

          if len(primary_keyword) > self.max_length:
              raise TextGenerationError(f"主要キーワードが長すぎます: {len(primary_keyword)}文字")

          if len(app_base_name) > self.max_length:
              raise TextGenerationError(f"アプリ基本名が長すぎます: {len(app_base_name)}文字")

          return True

      def _process_primary_keyword(self, keyword: str, language: str) -> str:
          """主要キーワードを処理"""
          # 空白除去と正規化
          processed = keyword.strip()

          # 言語に応じた処理
          if language == "ja":
              # 日本語の場合、全角文字を半角に変換
              processed = self._convert_fullwidth_to_halfwidth(processed)
          else:
              # 英語の場合、大文字小文字を調整
              processed = self._normalize_english_keyword(processed)

          # 特殊文字の除去
          processed = self._remove_special_chars(processed)

          return processed

      def _process_app_name(self, app_name: str, language: str) -> str:
          """アプリ基本名を処理"""
          # 空白除去と正規化
          processed = app_name.strip()

          # 言語に応じた処理
          if language == "ja":
              # 日本語の場合、全角文字を半角に変換
              processed = self._convert_fullwidth_to_halfwidth(processed)
          else:
              # 英語の場合、タイトルケースに変換
              processed = self._to_title_case(processed)

          # 特殊文字の除去
          processed = self._remove_special_chars(processed)

          # 長さの調整
          if len(processed) > self.max_app_name_length:
              processed = self._truncate_app_name(processed, self.max_app_name_length)

          return processed

      def _convert_fullwidth_to_halfwidth(self, text: str) -> str:
          """全角文字を半角に変換"""
          # 全角英数字を半角に変換
          fullwidth_chars = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
          halfwidth_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

          conversion_table = str.maketrans(fullwidth_chars, halfwidth_chars)
          return text.translate(conversion_table)

      def _normalize_english_keyword(self, keyword: str) -> str:
          """英語キーワードを正規化"""
          # 小文字に変換
          normalized = keyword.lower()
          # 各単語の最初の文字を大文字に
          normalized = normalized.title()
          return normalized

      def _to_title_case(self, text: str) -> str:
          """タイトルケースに変換"""
          return text.title()

      def _remove_special_chars(self, text: str) -> str:
          """特殊文字を除去"""
          # 禁止文字を除去
          forbidden_chars = ['<', '>', '&', '"', "'", '\\', '/', '|', '*', '?', ':', ';']
          for char in forbidden_chars:
              text = text.replace(char, '')

          # 連続する空白を単一の空白に
          text = re.sub(r'\s+', ' ', text)

          return text.strip()

      def _truncate_app_name(self, app_name: str, max_length: int) -> str:
          """アプリ名を切り詰め"""
          if len(app_name) <= max_length:
              return app_name

          # 単語境界で切り詰め
          truncated = app_name[:max_length]
          last_space = truncated.rfind(' ')

          if last_space > 0:
              return truncated[:last_space]

          return truncated

      def _get_separator(self, language: str) -> str:
          """言語に応じた区切り文字を取得"""
          separators = {
              "ja": " - ",
              "en": " - "
          }
          return separators.get(language, self.separator)

      def _build_title(self, keyword: str, separator: str, app_name: str) -> str:
          """タイトルを構築"""
          # 区切り文字の長さを考慮してタイトルを構築
          title = f"{keyword}{separator}{app_name}"

          # 30文字制限をチェック
          if len(title) > self.max_length:
              # アプリ名を短縮
              available_length = self.max_length - len(keyword) - len(separator)
              if available_length >= self.min_app_name_length:
                  app_name = self._truncate_app_name(app_name, available_length)
                  title = f"{keyword}{separator}{app_name}"
              else:
                  # キーワードのみでタイトルを構築
                  title = keyword[:self.max_length]

          return title

      def _validate_title(self, title: str) -> bool:
          """タイトルを検証"""
          if not title:
              raise TextGenerationError("タイトルが空です")

          if len(title) > self.max_length:
              raise TextGenerationError(f"タイトルが長すぎます: {len(title)}文字")

          # 禁止文字のチェック
          forbidden_chars = ['<', '>', '&', '"', "'"]
          for char in forbidden_chars:
              if char in title:
                  raise TextGenerationError(f"タイトルに禁止文字が含まれています: {char}")

          return True
  ```

- **多言語対応のタイトル処理**

  ```python
  class MultilingualTitleProcessor:
      """多言語対応タイトル処理クラス"""

      def __init__(self):
          self.language_rules = {
              "ja": {
                  "separator": " - ",
                  "max_keyword_length": 12,
                  "max_app_name_length": 15,
                  "case_sensitive": False
              },
              "en": {
                  "separator": " - ",
                  "max_keyword_length": 15,
                  "max_app_name_length": 12,
                  "case_sensitive": True
              }
          }

      def process_title_for_language(self, keyword: str, app_name: str, language: str) -> tuple[str, str]:
          """言語に応じたタイトル処理"""
          rules = self.language_rules.get(language, self.language_rules["en"])

          # キーワードの処理
          processed_keyword = self._process_keyword_for_language(keyword, rules)

          # アプリ名の処理
          processed_app_name = self._process_app_name_for_language(app_name, rules)

          return processed_keyword, processed_app_name

      def _process_keyword_for_language(self, keyword: str, rules: Dict[str, Any]) -> str:
          """言語に応じたキーワード処理"""
          processed = keyword.strip()

          # 長さ制限
          if len(processed) > rules["max_keyword_length"]:
              processed = processed[:rules["max_keyword_length"]]

          # 大文字小文字の処理
          if not rules["case_sensitive"]:
              processed = processed.lower()

          return processed

      def _process_app_name_for_language(self, app_name: str, rules: Dict[str, Any]) -> str:
          """言語に応じたアプリ名処理"""
          processed = app_name.strip()

          # 長さ制限
          if len(processed) > rules["max_app_name_length"]:
              processed = processed[:rules["max_app_name_length"]]

          # 大文字小文字の処理
          if rules["case_sensitive"]:
              processed = processed.title()

          return processed
  ```

- **統合タイトル生成サービス**

  ```python
  class TitleGenerationService:
      """統合タイトル生成サービス"""

      def __init__(self):
          self.generator = TitleGenerator()
          self.processor = MultilingualTitleProcessor()

      def generate_title(
          self,
          primary_keyword: str,
          app_base_name: str,
          language: str = "ja"
      ) -> Dict[str, Any]:
          """
          タイトルを生成（統合処理）

          Args:
              primary_keyword: 主要キーワード
              app_base_name: アプリ基本名
              language: 言語

          Returns:
              生成結果
          """
          try:
              # 入力データの検証
              if not primary_keyword or not app_base_name:
                  raise TextGenerationError("主要キーワードまたはアプリ基本名が空です")

              # 言語に応じた処理
              processed_keyword, processed_app_name = self.processor.process_title_for_language(
                  primary_keyword, app_base_name, language
              )

              # タイトルを生成
              title = self.generator.generate_title(
                  processed_keyword, processed_app_name, language
              )

              # 結果を構築
              result = {
                  'title': title,
                  'length': len(title),
                  'primary_keyword': primary_keyword,
                  'app_base_name': app_base_name,
                  'language': language,
                  'generated_at': datetime.now().isoformat()
              }

              return result

          except Exception as e:
              logger.error(f"タイトル生成サービスでエラーが発生しました: {str(e)}")
              raise TextGenerationError(f"タイトル生成に失敗しました: {str(e)}")
  ```

#### やらないこと（Out of Scope）

- 最新情報生成の実装（P2-003 で対応）
- Gemini 連携による生成（ステップ 3 で対応）
- データベースへの保存機能
- 外部 API との連携

#### 受入条件（Acceptance Criteria）

- 主要キーワードとアプリ基本名が適切に組み合わせられること
- 生成されたタイトルが 30 文字以内であること
- `「{主要キーワード} - {アプリ基本名}」` のテンプレートに従っていること
- 日本語・英語の両方で適切に生成されること
- 禁止文字が含まれていないこと
- アプリ基本名が長すぎる場合は適切に短縮されること
- エラーハンドリングが適切に動作すること
- 単体テストが実装され、カバレッジが 85%以上であること

#### 影響/変更ファイル

- 追加:
  - `app/services/title_generator.py` (タイトル生成サービス)
  - `tests/test_title_generator.py` (タイトル生成テスト)
- 変更:
  - `app/services/text_generator.py` (タイトル生成機能の統合)
  - `app/models/response_models.py` (タイトルレスポンスモデルの追加)

#### 依存関係 / ブロッカー

- **依存**: P2-001（キーワードフィールド生成）の完了
- **ブロッカー**: なし
- **後続**: P2-003（最新情報生成）は本チケットの完了に依存

#### 参考資料

- `docs/MVP開発ロードマップ.md` の「2-2. タイトル (30 文字) 生成」
- `docs/ASO戦略ルールまとめ.md` のタイトル生成ルール
- [App Store Connect ヘルプ](https://help.apple.com/app-store-connect/)

#### リスク / 留意点

- **文字数制限**: 30 文字制限の厳密な遵守
- **テンプレート準拠**: `「{主要キーワード} - {アプリ基本名}」` テンプレートの正確な実装
- **多言語対応**: 日本語・英語の言語特性の違い
- **アプリ名短縮**: 長いアプリ名の適切な短縮処理
- **特殊文字処理**: 禁止文字の適切な除去

#### 見積り

- 3 時間（計画準拠）
  - タイトル生成アルゴリズム実装: 1.5 時間
  - 多言語対応機能実装: 1 時間
  - テスト実装: 0.5 時間
