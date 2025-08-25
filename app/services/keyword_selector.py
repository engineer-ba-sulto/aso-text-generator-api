"""
キーワード選定サービス
キーワードの選定と優先度付けを行うサービス
"""

import logging
from typing import Any, Dict, List, Optional

from app.models.csv_models import KeywordData
from app.services.keyword_scorer import KeywordScoringService, ScoringResult
from app.utils.exceptions import KeywordSelectionError

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
                logger.warning(
                    f"最高スコアが閾値を下回っています: {primary_result.composite_score}"
                )
                # 閾値を下回る場合は警告を出すが、処理は継続

            # 選定結果を構築
            selection_result = {
                "primary_keyword": primary_result.keyword,
                "primary_score": primary_result.composite_score,
                "primary_ranking": primary_result.ranking,
                "primary_popularity": primary_result.popularity,
                "primary_difficulty": primary_result.difficulty,
                "component_scores": {
                    "ranking_score": primary_result.ranking_score,
                    "popularity_score": primary_result.popularity_score,
                    "difficulty_score": primary_result.difficulty_score,
                },
                "candidates": self._get_top_candidates(scoring_results),
                "total_keywords_analyzed": len(keywords),
            }

            logger.info(
                f"主要キーワードを選定しました: {primary_result.keyword} (スコア: {primary_result.composite_score})"
            )

            return selection_result

        except Exception as e:
            logger.error(f"主要キーワード選定中にエラーが発生しました: {str(e)}")
            raise KeywordSelectionError(f"主要キーワード選定に失敗しました: {str(e)}")

    def _get_top_candidates(
        self, scoring_results: List[ScoringResult]
    ) -> List[Dict[str, Any]]:
        """
        上位候補キーワードを取得

        Args:
            scoring_results: スコアリング結果のリスト

        Returns:
            上位候補のリスト
        """
        candidates = []
        top_results = scoring_results[: self.max_keywords_to_consider]

        for i, result in enumerate(top_results):
            candidate = {
                "rank": i + 1,
                "keyword": result.keyword,
                "score": result.composite_score,
                "ranking": result.ranking,
                "popularity": result.popularity,
                "difficulty": result.difficulty,
            }
            candidates.append(candidate)

        return candidates


class KeywordSelectionValidator:
    """キーワード選定結果検証クラス"""

    def __init__(self):
        self.min_keyword_length = 2  # 最小キーワード長
        self.max_keyword_length = 50  # 最大キーワード長
        self.forbidden_chars = ["<", ">", "&", '"', "'"]  # 禁止文字

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
                raise KeywordSelectionError(
                    f"キーワードに禁止文字が含まれています: {char}"
                )

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
            "primary_keyword",
            "primary_score",
            "primary_ranking",
            "primary_popularity",
            "primary_difficulty",
            "candidates",
        ]

        for field in required_fields:
            if field not in result:
                raise KeywordSelectionError(f"必須フィールドが不足しています: {field}")

        # 主要キーワードの妥当性を検証
        self.validate_primary_keyword(result["primary_keyword"])

        # スコアの妥当性を検証
        if not (0 <= result["primary_score"] <= 1):
            raise KeywordSelectionError(
                f"スコアが不正な値です: {result['primary_score']}"
            )

        return True


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
        primary = result["primary_keyword"]
        score = result["primary_score"]
        ranking = result["primary_ranking"]
        popularity = result["primary_popularity"]
        difficulty = result["primary_difficulty"]
        total = result["total_keywords_analyzed"]

        summary = (
            f"主要キーワード: {primary}\n"
            f"スコア: {score:.4f}\n"
            f"ランキング: {ranking}位\n"
            f"人気度: {popularity:.1f}\n"
            f"難易度: {difficulty:.1f}\n"
            f"分析対象キーワード数: {total}"
        )

        return summary


# 後方互換性のためのエイリアス
KeywordSelector = KeywordSelectionService
