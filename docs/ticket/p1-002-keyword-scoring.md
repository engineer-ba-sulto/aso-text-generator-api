### チケット: P1-002 キーワードスコアリング

#### 背景 / 目的

- **背景**: CSV データモデルとバリデーション機能は実装済みだが、各キーワードの評価スコアを算出する機能が未実装
- **目的**: 各キーワードに対し、ランキング、人気度、難易度を組み合わせた評価スコアを算出し、主要キーワード選定の基盤を構築する

#### スコープ（このチケットでやること）

- **キーワードスコアリングアルゴリズムの実装**

  ```python
  # app/services/keyword_scorer.py
  from typing import List, Dict, Any
  import numpy as np
  from app.models.csv_models import KeywordData

  class KeywordScorer:
      """キーワードスコアリングクラス"""

      def __init__(self, ranking_weight: float = 0.4, popularity_weight: float = 0.4, difficulty_weight: float = 0.2):
          """
          初期化

          Args:
              ranking_weight: ランキングの重み（デフォルト: 0.4）
              popularity_weight: 人気度の重み（デフォルト: 0.4）
              difficulty_weight: 難易度の重み（デフォルト: 0.2）
          """
          self.ranking_weight = ranking_weight
          self.popularity_weight = popularity_weight
          self.difficulty_weight = difficulty_weight

          # 重みの合計が1.0になることを確認
          total_weight = ranking_weight + popularity_weight + difficulty_weight
          if abs(total_weight - 1.0) > 0.001:
              raise ValueError("重みの合計は1.0である必要があります")

      def calculate_ranking_score(self, ranking: int) -> float:
          """
          ランキングスコアを計算（1位が最高スコア）

          Args:
              ranking: ランキング（1-1000）

          Returns:
              正規化されたランキングスコア（0-1）
          """
          # ランキングが低いほど高スコア（1位が1.0、1000位が0.0）
          return max(0.0, (1000 - ranking) / 999)

      def calculate_popularity_score(self, popularity: float) -> float:
          """
          人気度スコアを計算

          Args:
              popularity: 人気度（0-100）

          Returns:
              正規化された人気度スコア（0-1）
          """
          return popularity / 100.0

      def calculate_difficulty_score(self, difficulty: float) -> float:
          """
          難易度スコアを計算（難易度が低いほど高スコア）

          Args:
              difficulty: 難易度（0-100）

          Returns:
              正規化された難易度スコア（0-1）
          """
          # 難易度が低いほど高スコア
          return (100 - difficulty) / 100.0

      def calculate_composite_score(self, keyword_data: KeywordData) -> float:
          """
          複合スコアを計算

          Args:
              keyword_data: キーワードデータ

          Returns:
              複合スコア（0-1）
          """
          ranking_score = self.calculate_ranking_score(keyword_data.ranking)
          popularity_score = self.calculate_popularity_score(keyword_data.popularity)
          difficulty_score = self.calculate_difficulty_score(keyword_data.difficulty)

          composite_score = (
              self.ranking_weight * ranking_score +
              self.popularity_weight * popularity_score +
              self.difficulty_weight * difficulty_score
          )

          return round(composite_score, 4)
  ```

- **スコアリング結果の管理**

  ```python
  class ScoringResult:
      """スコアリング結果クラス"""

      def __init__(self, keyword_data: KeywordData, composite_score: float):
          self.keyword_data = keyword_data
          self.composite_score = composite_score
          self.ranking_score = None
          self.popularity_score = None
          self.difficulty_score = None

      def set_component_scores(self, ranking_score: float, popularity_score: float, difficulty_score: float):
          """各要素スコアを設定"""
          self.ranking_score = ranking_score
          self.popularity_score = popularity_score
          self.difficulty_score = difficulty_score

  class KeywordScoringService:
      """キーワードスコアリングサービス"""

      def __init__(self):
          self.scorer = KeywordScorer()

      def score_keywords(self, keywords: List[KeywordData]) -> List[ScoringResult]:
          """
          キーワードリストをスコアリング

          Args:
              keywords: キーワードデータのリスト

          Returns:
              スコアリング結果のリスト（スコア降順）
          """
          results = []

          for keyword_data in keywords:
              # 複合スコアを計算
              composite_score = self.scorer.calculate_composite_score(keyword_data)

              # 結果オブジェクトを作成
              result = ScoringResult(keyword_data, composite_score)

              # 各要素スコアを設定
              ranking_score = self.scorer.calculate_ranking_score(keyword_data.ranking)
              popularity_score = self.scorer.calculate_popularity_score(keyword_data.popularity)
              difficulty_score = self.scorer.calculate_difficulty_score(keyword_data.difficulty)
              result.set_component_scores(ranking_score, popularity_score, difficulty_score)

              results.append(result)

          # スコア降順でソート
          results.sort(key=lambda x: x.composite_score, reverse=True)

          return results
  ```

- **スコアリング結果のキャッシュ機能**

  ```python
  from functools import lru_cache
  import hashlib
  import json

  class CachedKeywordScoringService(KeywordScoringService):
      """キャッシュ機能付きキーワードスコアリングサービス"""

      def __init__(self, cache_size: int = 100):
          super().__init__()
          self.cache_size = cache_size

      @lru_cache(maxsize=100)
      def _get_cache_key(self, keywords_hash: str) -> str:
          """キャッシュキーを生成"""
          return keywords_hash

      def _hash_keywords(self, keywords: List[KeywordData]) -> str:
          """キーワードリストのハッシュを生成"""
          # キーワードデータをハッシュ化可能な形式に変換
          keywords_data = []
          for kw in keywords:
              keywords_data.append({
                  'keyword': kw.keyword,
                  'ranking': kw.ranking,
                  'popularity': kw.popularity,
                  'difficulty': kw.difficulty
              })

          # JSON文字列に変換してハッシュ化
          json_str = json.dumps(keywords_data, sort_keys=True)
          return hashlib.md5(json_str.encode()).hexdigest()

      def score_keywords(self, keywords: List[KeywordData]) -> List[ScoringResult]:
          """
          キャッシュ機能付きキーワードスコアリング

          Args:
              keywords: キーワードデータのリスト

          Returns:
              スコアリング結果のリスト
          """
          # キャッシュキーを生成
          keywords_hash = self._hash_keywords(keywords)

          # キャッシュから結果を取得（実装は簡略化）
          # 実際の実装では Redis やメモリキャッシュを使用

          # スコアリング実行
          results = super().score_keywords(keywords)

          return results
  ```

#### やらないこと（Out of Scope）

- 主要キーワード選定の実装（P1-003 で対応）
- データベースへの保存機能
- リアルタイムでのスコア更新機能
- 外部 API との連携

#### 受入条件（Acceptance Criteria）

- 各キーワードの複合スコアが正確に計算されること
- ランキング、人気度、難易度の重み付けが正しく適用されること
- スコアリング結果がスコア降順でソートされること
- 各要素スコア（ランキング、人気度、難易度）が個別に取得できること
- キャッシュ機能が正常に動作すること
- 単体テストが実装され、カバレッジが 85%以上であること

#### 影響/変更ファイル

- 追加:
  - `app/services/keyword_scorer.py` (キーワードスコアリングサービス)
  - `tests/test_keyword_scorer.py` (スコアリングテスト)
- 変更:
  - `app/models/csv_models.py` (スコアリング結果モデルの追加)
  - `app/services/csv_analyzer.py` (スコアリング機能の統合)

#### 依存関係 / ブロッカー

- **依存**: P1-001（CSV データモデルとバリデーション）の完了
- **ブロッカー**: なし
- **後続**: P1-003（主要キーワード自動選定）は本チケットの完了に依存

#### 参考資料

- `docs/MVP開発ロードマップ.md` の「1-2. キーワードスコアリング」
- `docs/ASO戦略ルールまとめ.md` のスコアリングルール
- [NumPy 公式ドキュメント](https://numpy.org/doc/)

#### リスク / 留意点

- **重み付けパラメータ**: ランキング、人気度、難易度の重み付けバランスの調整
- **スコア正規化**: 各要素のスコア正規化方法の妥当性
- **パフォーマンス**: 大量キーワードのスコアリング処理時間
- **キャッシュ戦略**: 適切なキャッシュサイズと無効化戦略

#### 見積り

- 5 時間（計画準拠）
  - スコアリングアルゴリズム実装: 2.5 時間
  - キャッシュ機能実装: 1.5 時間
  - テスト実装: 1 時間
