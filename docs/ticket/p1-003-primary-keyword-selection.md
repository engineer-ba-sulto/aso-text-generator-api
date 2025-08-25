### チケット: P1-003 主要キーワードの自動選定

#### 背景 / 目的

- **背景**: キーワードスコアリング機能は実装済みだが、スコアが最も高いキーワードを「単一主要キーワード」として自動選定する機能が未実装
- **目的**: スコアリング結果に基づいて最適な主要キーワードを自動選定し、後続のテキスト生成機能の基盤を構築する

#### スコープ（このチケットでやること）

- **主要キーワード選定ロジックの実装**

  ```python
  # app/services/keyword_selector.py
  from typing import List, Optional, Dict, Any
  from app.services.keyword_scorer import ScoringResult, KeywordScoringService
  from app.models.csv_models import KeywordData
  from app.utils.exceptions import KeywordSelectionError
  import logging

  logger = logging.getLogger(__name__)

  class PrimaryKeywordSelector:
      """主要キーワード選定クラス"""

      def __init__(self, scoring_service: KeywordScoringService):
          """
          初期化

          Args:
              scoring_service: キーワードスコアリングサービス
          """
          self.scoring_service = scoring_service
          self.min_score_threshold = 0.3  # 最小スコア閾値
          self.max_keywords_to_consider = 10  # 考慮する上位キーワード数

      def select_primary_keyword(self, keywords: List[KeywordData]) -> Dict[str, Any]:
          """
          主要キーワードを選定

          Args:
              keywords: キーワードデータのリスト

          Returns:
              選定結果の辞書
          """
          try:
              # キーワードをスコアリング
              scoring_results = self.scoring_service.score_keywords(keywords)

              if not scoring_results:
                  raise KeywordSelectionError("スコアリング結果が空です")

              # 最高スコアのキーワードを取得
              primary_result = scoring_results[0]

              # スコア閾値チェック
              if primary_result.composite_score < self.min_score_threshold:
                  logger.warning(f"最高スコアが閾値を下回っています: {primary_result.composite_score}")
                  # 閾値を下回る場合は警告を出すが、処理は継続

              # 選定結果を構築
              selection_result = {
                  'primary_keyword': primary_result.keyword_data.keyword,
                  'primary_score': primary_result.composite_score,
                  'primary_ranking': primary_result.keyword_data.ranking,
                  'primary_popularity': primary_result.keyword_data.popularity,
                  'primary_difficulty': primary_result.keyword_data.difficulty,
                  'component_scores': {
                      'ranking_score': primary_result.ranking_score,
                      'popularity_score': primary_result.popularity_score,
                      'difficulty_score': primary_result.difficulty_score
                  },
                  'candidates': self._get_top_candidates(scoring_results),
                  'total_keywords_analyzed': len(keywords)
              }

              logger.info(f"主要キーワードを選定しました: {primary_result.keyword_data.keyword} (スコア: {primary_result.composite_score})")

              return selection_result

          except Exception as e:
              logger.error(f"主要キーワード選定中にエラーが発生しました: {str(e)}")
              raise KeywordSelectionError(f"主要キーワード選定に失敗しました: {str(e)}")

      def _get_top_candidates(self, scoring_results: List[ScoringResult]) -> List[Dict[str, Any]]:
          """
          上位候補キーワードを取得

          Args:
              scoring_results: スコアリング結果のリスト

          Returns:
              上位候補のリスト
          """
          candidates = []
          top_results = scoring_results[:self.max_keywords_to_consider]

          for i, result in enumerate(top_results):
              candidate = {
                  'rank': i + 1,
                  'keyword': result.keyword_data.keyword,
                  'score': result.composite_score,
                  'ranking': result.keyword_data.ranking,
                  'popularity': result.keyword_data.popularity,
                  'difficulty': result.keyword_data.difficulty
              }
              candidates.append(candidate)

          return candidates
  ```

- **選定結果の検証機能**

  ```python
  class KeywordSelectionValidator:
      """キーワード選定結果検証クラス"""

      def __init__(self):
          self.min_keyword_length = 2  # 最小キーワード長
          self.max_keyword_length = 50  # 最大キーワード長
          self.forbidden_chars = ['<', '>', '&', '"', "'"]  # 禁止文字

      def validate_primary_keyword(self, keyword: str) -> bool:
          """
          主要キーワードの妥当性を検証

          Args:
              keyword: 検証対象のキーワード

          Returns:
              妥当性チェック結果
          """
          # 長さチェック
          if len(keyword) < self.min_keyword_length:
              raise KeywordSelectionError(f"キーワードが短すぎます: {keyword}")

          if len(keyword) > self.max_keyword_length:
              raise KeywordSelectionError(f"キーワードが長すぎます: {keyword}")

          # 禁止文字チェック
          for char in self.forbidden_chars:
              if char in keyword:
                  raise KeywordSelectionError(f"キーワードに禁止文字が含まれています: {char}")

          # 空白文字チェック
          if keyword.strip() != keyword:
              raise KeywordSelectionError("キーワードの前後に空白文字が含まれています")

          return True

      def validate_selection_result(self, result: Dict[str, Any]) -> bool:
          """
          選定結果全体の妥当性を検証

          Args:
              result: 選定結果の辞書

          Returns:
              妥当性チェック結果
          """
          required_fields = [
              'primary_keyword', 'primary_score', 'primary_ranking',
              'primary_popularity', 'primary_difficulty', 'candidates'
          ]

          for field in required_fields:
              if field not in result:
                  raise KeywordSelectionError(f"必須フィールドが不足しています: {field}")

          # 主要キーワードの妥当性を検証
          self.validate_primary_keyword(result['primary_keyword'])

          # スコアの妥当性を検証
          if not (0 <= result['primary_score'] <= 1):
              raise KeywordSelectionError(f"スコアが不正な値です: {result['primary_score']}")

          return True
  ```

- **統合キーワード選定サービス**

  ```python
  class KeywordSelectionService:
      """統合キーワード選定サービス"""

      def __init__(self):
          self.scoring_service = KeywordScoringService()
          self.selector = PrimaryKeywordSelector(self.scoring_service)
          self.validator = KeywordSelectionValidator()

      def select_primary_keyword(self, keywords: List[KeywordData]) -> Dict[str, Any]:
          """
          主要キーワードを選定（統合処理）

          Args:
              keywords: キーワードデータのリスト

          Returns:
              検証済み選定結果
          """
          # 入力データの検証
          if not keywords:
              raise KeywordSelectionError("キーワードリストが空です")

          if len(keywords) > 1000:
              raise KeywordSelectionError("キーワード数が上限を超えています")

          # 主要キーワードを選定
          selection_result = self.selector.select_primary_keyword(keywords)

          # 選定結果を検証
          self.validator.validate_selection_result(selection_result)

          return selection_result

      def get_selection_summary(self, result: Dict[str, Any]) -> str:
          """
          選定結果のサマリーを生成

          Args:
              result: 選定結果

          Returns:
              サマリーテキスト
          """
          primary = result['primary_keyword']
          score = result['primary_score']
          ranking = result['primary_ranking']
          popularity = result['primary_popularity']
          difficulty = result['primary_difficulty']
          total = result['total_keywords_analyzed']

          summary = (
              f"主要キーワード: {primary}\n"
              f"スコア: {score:.4f}\n"
              f"ランキング: {ranking}位\n"
              f"人気度: {popularity:.1f}\n"
              f"難易度: {difficulty:.1f}\n"
              f"分析対象キーワード数: {total}"
          )

          return summary
  ```

#### やらないこと（Out of Scope）

- テキスト生成機能の実装（ステップ 2 で対応）
- データベースへの保存機能
- リアルタイムでの選定結果更新機能
- 外部 API との連携

#### 受入条件（Acceptance Criteria）

- スコアが最も高いキーワードが正しく選定されること
- 選定結果に必要な情報（キーワード、スコア、ランキング、人気度、難易度）が含まれること
- 上位候補キーワードのリストが取得できること
- 選定結果の妥当性検証が正常に動作すること
- エラーハンドリングとフォールバック機能が適切に動作すること
- ログ出力が適切に行われること
- 単体テストが実装され、カバレッジが 80%以上であること

#### 影響/変更ファイル

- 追加:
  - `app/services/keyword_selector.py` (キーワード選定サービス)
  - `tests/test_keyword_selector.py` (キーワード選定テスト)
- 変更:
  - `app/models/csv_models.py` (選定結果モデルの追加)
  - `app/services/csv_analyzer.py` (選定機能の統合)
  - `app/utils/exceptions.py` (選定関連例外の追加)

#### 依存関係 / ブロッカー

- **依存**: P1-002（キーワードスコアリング）の完了
- **ブロッカー**: なし
- **後続**: ステップ 2（テキスト生成機能）は本チケットの完了に依存

#### 参考資料

- `docs/MVP開発ロードマップ.md` の「1-3. 主要キーワードの自動選定」
- `docs/ASO戦略ルールまとめ.md` のキーワード選定ルール
- `docs/PRD.md` の主要キーワード要件

#### リスク / 留意点

- **スコア閾値**: 最小スコア閾値の適切な設定
- **同点処理**: 同じスコアのキーワードが複数存在する場合の処理
- **データ品質**: 不正なデータによる選定結果への影響
- **パフォーマンス**: 大量キーワードの選定処理時間
- **ログ管理**: 選定プロセスの追跡可能性

#### 見積り

- 3 時間（計画準拠）
  - 選定ロジック実装: 1.5 時間
  - 検証機能実装: 1 時間
  - テスト実装: 0.5 時間
