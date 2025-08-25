"""
キーワード選定機能のテスト
"""

from unittest.mock import Mock, patch

import pytest

from app.models.csv_models import KeywordData
from app.services.keyword_scorer import KeywordScoringService, ScoringResult
from app.services.keyword_selector import (
    KeywordSelectionService,
    KeywordSelectionValidator,
    PrimaryKeywordSelector,
)
from app.utils.exceptions import KeywordSelectionError


class TestPrimaryKeywordSelector:
    """主要キーワード選定クラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.mock_scoring_service = Mock(spec=KeywordScoringService)
        self.selector = PrimaryKeywordSelector(self.mock_scoring_service)

    def test_select_primary_keyword_success(self):
        """主要キーワード選定の成功テスト"""
        # テストデータの準備
        keywords = [
            KeywordData(
                keyword="テストキーワード1", ranking=1, popularity=80.0, difficulty=30.0
            ),
            KeywordData(
                keyword="テストキーワード2", ranking=5, popularity=60.0, difficulty=50.0
            ),
        ]

        # モックの設定
        mock_result1 = Mock(spec=ScoringResult)
        mock_result1.keyword_data = keywords[0]
        mock_result1.composite_score = 0.85
        mock_result1.ranking_score = 0.9
        mock_result1.popularity_score = 0.8
        mock_result1.difficulty_score = 0.7

        mock_result2 = Mock(spec=ScoringResult)
        mock_result2.keyword_data = keywords[1]
        mock_result2.composite_score = 0.65
        mock_result2.ranking_score = 0.7
        mock_result2.popularity_score = 0.6
        mock_result2.difficulty_score = 0.5

        self.mock_scoring_service.score_keywords.return_value = [
            mock_result1,
            mock_result2,
        ]

        # テスト実行
        result = self.selector.select_primary_keyword(keywords)

        # 検証
        assert result["primary_keyword"] == "テストキーワード1"
        assert result["primary_score"] == 0.85
        assert result["primary_ranking"] == 1
        assert result["primary_popularity"] == 80.0
        assert result["primary_difficulty"] == 30.0
        assert result["total_keywords_analyzed"] == 2
        assert len(result["candidates"]) == 2

    def test_select_primary_keyword_empty_results(self):
        """空のスコアリング結果のテスト"""
        keywords = [
            KeywordData(
                keyword="テストキーワード", ranking=1, popularity=80.0, difficulty=30.0
            )
        ]
        self.mock_scoring_service.score_keywords.return_value = []

        with pytest.raises(KeywordSelectionError, match="スコアリング結果が空です"):
            self.selector.select_primary_keyword(keywords)

    def test_select_primary_keyword_low_score_warning(self):
        """低スコア警告のテスト"""
        keywords = [
            KeywordData(
                keyword="テストキーワード", ranking=1, popularity=80.0, difficulty=30.0
            )
        ]

        mock_result = Mock(spec=ScoringResult)
        mock_result.keyword_data = keywords[0]
        mock_result.composite_score = 0.2  # 閾値以下
        mock_result.ranking_score = 0.3
        mock_result.popularity_score = 0.2
        mock_result.difficulty_score = 0.1

        self.mock_scoring_service.score_keywords.return_value = [mock_result]

        # 警告が出ても処理は継続されることを確認
        result = self.selector.select_primary_keyword(keywords)
        assert result["primary_keyword"] == "テストキーワード"

    def test_get_top_candidates(self):
        """上位候補取得のテスト"""
        keywords = [
            KeywordData(
                keyword="キーワード1", ranking=1, popularity=80.0, difficulty=30.0
            ),
            KeywordData(
                keyword="キーワード2", ranking=2, popularity=70.0, difficulty=40.0
            ),
            KeywordData(
                keyword="キーワード3", ranking=3, popularity=60.0, difficulty=50.0
            ),
        ]

        mock_results = []
        for i, kw in enumerate(keywords):
            mock_result = Mock(spec=ScoringResult)
            mock_result.keyword_data = kw
            mock_result.composite_score = 0.9 - (i * 0.1)
            mock_results.append(mock_result)

        candidates = self.selector._get_top_candidates(mock_results)

        assert len(candidates) == 3
        assert candidates[0]["rank"] == 1
        assert candidates[0]["keyword"] == "キーワード1"
        assert candidates[0]["score"] == 0.9


class TestKeywordSelectionValidator:
    """キーワード選定結果検証クラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.validator = KeywordSelectionValidator()

    def test_validate_primary_keyword_success(self):
        """主要キーワード検証の成功テスト"""
        valid_keyword = "正常なキーワード"
        assert self.validator.validate_primary_keyword(valid_keyword) is True

    def test_validate_primary_keyword_too_short(self):
        """短すぎるキーワードのテスト"""
        with pytest.raises(KeywordSelectionError, match="キーワードが短すぎます"):
            self.validator.validate_primary_keyword("a")

    def test_validate_primary_keyword_too_long(self):
        """長すぎるキーワードのテスト"""
        long_keyword = "a" * 51
        with pytest.raises(KeywordSelectionError, match="キーワードが長すぎます"):
            self.validator.validate_primary_keyword(long_keyword)

    def test_validate_primary_keyword_forbidden_chars(self):
        """禁止文字を含むキーワードのテスト"""
        with pytest.raises(
            KeywordSelectionError, match="キーワードに禁止文字が含まれています"
        ):
            self.validator.validate_primary_keyword("テスト<キーワード>")

    def test_validate_primary_keyword_whitespace(self):
        """空白文字を含むキーワードのテスト"""
        with pytest.raises(
            KeywordSelectionError, match="キーワードの前後に空白文字が含まれています"
        ):
            self.validator.validate_primary_keyword(" テストキーワード ")

    def test_validate_selection_result_success(self):
        """選定結果検証の成功テスト"""
        valid_result = {
            "primary_keyword": "テストキーワード",
            "primary_score": 0.8,
            "primary_ranking": 1,
            "primary_popularity": 80.0,
            "primary_difficulty": 30.0,
            "candidates": [],
        }
        assert self.validator.validate_selection_result(valid_result) is True

    def test_validate_selection_result_missing_field(self):
        """必須フィールド不足のテスト"""
        invalid_result = {
            "primary_keyword": "テストキーワード",
            "primary_score": 0.8,
            # 他の必須フィールドが不足
        }
        with pytest.raises(
            KeywordSelectionError, match="必須フィールドが不足しています"
        ):
            self.validator.validate_selection_result(invalid_result)

    def test_validate_selection_result_invalid_score(self):
        """不正なスコアのテスト"""
        invalid_result = {
            "primary_keyword": "テストキーワード",
            "primary_score": 1.5,  # 範囲外
            "primary_ranking": 1,
            "primary_popularity": 80.0,
            "primary_difficulty": 30.0,
            "candidates": [],
        }
        with pytest.raises(KeywordSelectionError, match="スコアが不正な値です"):
            self.validator.validate_selection_result(invalid_result)


class TestKeywordSelectionService:
    """統合キーワード選定サービスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.service = KeywordSelectionService()

    def test_select_primary_keyword_success(self):
        """主要キーワード選定の成功テスト"""
        keywords = [
            KeywordData(
                keyword="テストキーワード1", ranking=1, popularity=80.0, difficulty=30.0
            ),
            KeywordData(
                keyword="テストキーワード2", ranking=5, popularity=60.0, difficulty=50.0
            ),
        ]

        result = self.service.select_primary_keyword(keywords)

        assert "primary_keyword" in result
        assert "primary_score" in result
        assert "primary_ranking" in result
        assert "primary_popularity" in result
        assert "primary_difficulty" in result
        assert "component_scores" in result
        assert "candidates" in result
        assert "total_keywords_analyzed" in result
        assert result["total_keywords_analyzed"] == 2

    def test_select_primary_keyword_empty_list(self):
        """空リストのテスト"""
        with pytest.raises(KeywordSelectionError, match="キーワードリストが空です"):
            self.service.select_primary_keyword([])

    def test_select_primary_keyword_too_many_keywords(self):
        """キーワード数上限超過のテスト"""
        keywords = [
            KeywordData(
                keyword=f"キーワード{i}", ranking=1, popularity=80.0, difficulty=30.0
            )
            for i in range(1001)
        ]
        with pytest.raises(
            KeywordSelectionError, match="キーワード数が上限を超えています"
        ):
            self.service.select_primary_keyword(keywords)

    def test_get_selection_summary(self):
        """選定結果サマリー生成のテスト"""
        result = {
            "primary_keyword": "テストキーワード",
            "primary_score": 0.85,
            "primary_ranking": 1,
            "primary_popularity": 80.0,
            "primary_difficulty": 30.0,
            "total_keywords_analyzed": 10,
        }

        summary = self.service.get_selection_summary(result)

        assert "主要キーワード: テストキーワード" in summary
        assert "スコア: 0.8500" in summary
        assert "ランキング: 1位" in summary
        assert "人気度: 80.0" in summary
        assert "難易度: 30.0" in summary
        assert "分析対象キーワード数: 10" in summary
