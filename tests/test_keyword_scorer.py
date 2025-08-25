import numpy as np
import pytest

from app.models.csv_models import KeywordData, PydanticScoringResult, ScoringResults
from app.services.keyword_scorer import (
    CachedKeywordScoringService,
    KeywordScorer,
    KeywordScoringService,
    ScoringResult,
)


class TestKeywordScorer:
    """キーワードスコアリングクラスのテスト"""

    def test_init_valid_weights(self):
        """正常な重みでの初期化テスト"""
        scorer = KeywordScorer(0.4, 0.4, 0.2)
        assert scorer.ranking_weight == 0.4
        assert scorer.popularity_weight == 0.4
        assert scorer.difficulty_weight == 0.2

    def test_init_invalid_weights(self):
        """不正な重みでの初期化テスト"""
        with pytest.raises(ValueError) as exc_info:
            KeywordScorer(0.5, 0.5, 0.5)  # 合計が1.5
        assert "重みの合計は1.0である必要があります" in str(exc_info.value)

    def test_calculate_ranking_score_first_place(self):
        """1位のランキングスコア計算テスト"""
        scorer = KeywordScorer()
        score = scorer.calculate_ranking_score(1)
        assert score == 1.0

    def test_calculate_ranking_score_last_place(self):
        """1000位のランキングスコア計算テスト"""
        scorer = KeywordScorer()
        score = scorer.calculate_ranking_score(1000)
        assert score == 0.0

    def test_calculate_ranking_score_middle_place(self):
        """中間順位のランキングスコア計算テスト"""
        scorer = KeywordScorer()
        score = scorer.calculate_ranking_score(500)
        expected_score = (1000 - 500) / 999
        assert abs(score - expected_score) < 0.001

    def test_calculate_popularity_score_max(self):
        """最大人気度のスコア計算テスト"""
        scorer = KeywordScorer()
        score = scorer.calculate_popularity_score(100.0)
        assert score == 1.0

    def test_calculate_popularity_score_min(self):
        """最小人気度のスコア計算テスト"""
        scorer = KeywordScorer()
        score = scorer.calculate_popularity_score(0.0)
        assert score == 0.0

    def test_calculate_popularity_score_middle(self):
        """中間人気度のスコア計算テスト"""
        scorer = KeywordScorer()
        score = scorer.calculate_popularity_score(50.0)
        assert score == 0.5

    def test_calculate_difficulty_score_easy(self):
        """簡単な難易度のスコア計算テスト"""
        scorer = KeywordScorer()
        score = scorer.calculate_difficulty_score(0.0)
        assert score == 1.0

    def test_calculate_difficulty_score_hard(self):
        """難しい難易度のスコア計算テスト"""
        scorer = KeywordScorer()
        score = scorer.calculate_difficulty_score(100.0)
        assert score == 0.0

    def test_calculate_difficulty_score_middle(self):
        """中間難易度のスコア計算テスト"""
        scorer = KeywordScorer()
        score = scorer.calculate_difficulty_score(50.0)
        assert score == 0.5

    def test_calculate_composite_score(self):
        """複合スコア計算テスト"""
        scorer = KeywordScorer(0.4, 0.4, 0.2)
        keyword_data = KeywordData(
            keyword="test_keyword",
            ranking=1,  # ランキングスコア: 1.0
            popularity=100.0,  # 人気度スコア: 1.0
            difficulty=0.0,  # 難易度スコア: 1.0
        )

        composite_score = scorer.calculate_composite_score(keyword_data)
        expected_score = 0.4 * 1.0 + 0.4 * 1.0 + 0.2 * 1.0
        assert abs(composite_score - expected_score) < 0.001

    def test_calculate_composite_score_with_different_weights(self):
        """異なる重みでの複合スコア計算テスト"""
        scorer = KeywordScorer(0.6, 0.3, 0.1)
        keyword_data = KeywordData(
            keyword="test_keyword",
            ranking=100,  # ランキングスコア: (1000-100)/999 ≈ 0.9
            popularity=50.0,  # 人気度スコア: 0.5
            difficulty=50.0,  # 難易度スコア: 0.5
        )

        composite_score = scorer.calculate_composite_score(keyword_data)
        ranking_score = (1000 - 100) / 999
        expected_score = 0.6 * ranking_score + 0.3 * 0.5 + 0.1 * 0.5
        assert abs(composite_score - expected_score) < 0.001


class TestScoringResult:
    """スコアリング結果クラスのテスト"""

    def test_init(self):
        """初期化テスト"""
        keyword_data = KeywordData(
            keyword="test", ranking=1, popularity=50.0, difficulty=30.0
        )
        result = ScoringResult(keyword_data, 0.8)

        assert result.keyword_data == keyword_data
        assert result.composite_score == 0.8
        assert result.ranking_score is None
        assert result.popularity_score is None
        assert result.difficulty_score is None

    def test_set_component_scores(self):
        """要素スコア設定テスト"""
        keyword_data = KeywordData(
            keyword="test", ranking=1, popularity=50.0, difficulty=30.0
        )
        result = ScoringResult(keyword_data, 0.8)

        result.set_component_scores(0.9, 0.7, 0.6)

        assert result.ranking_score == 0.9
        assert result.popularity_score == 0.7
        assert result.difficulty_score == 0.6


class TestKeywordScoringService:
    """キーワードスコアリングサービスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.service = KeywordScoringService()

    def test_score_keywords_single(self):
        """単一キーワードのスコアリングテスト"""
        keywords = [
            KeywordData(keyword="test1", ranking=1, popularity=100.0, difficulty=0.0)
        ]

        results = self.service.score_keywords(keywords)

        assert len(results) == 1
        assert results[0].keyword_data.keyword == "test1"
        assert results[0].composite_score > 0.9  # 高スコアになるはず
        assert results[0].ranking_score == 1.0
        assert results[0].popularity_score == 1.0
        assert results[0].difficulty_score == 1.0

    def test_score_keywords_multiple_sorted(self):
        """複数キーワードのスコアリングとソートテスト"""
        keywords = [
            KeywordData(
                keyword="low_score", ranking=1000, popularity=0.0, difficulty=100.0
            ),
            KeywordData(
                keyword="high_score", ranking=1, popularity=100.0, difficulty=0.0
            ),
            KeywordData(
                keyword="medium_score", ranking=500, popularity=50.0, difficulty=50.0
            ),
        ]

        results = self.service.score_keywords(keywords)

        assert len(results) == 3
        # スコア降順でソートされていることを確認
        assert results[0].composite_score >= results[1].composite_score
        assert results[1].composite_score >= results[2].composite_score
        assert results[0].keyword_data.keyword == "high_score"
        assert results[2].keyword_data.keyword == "low_score"

    def test_score_keywords_component_scores(self):
        """要素スコアの設定テスト"""
        keywords = [
            KeywordData(keyword="test", ranking=100, popularity=50.0, difficulty=30.0)
        ]

        results = self.service.score_keywords(keywords)

        assert len(results) == 1
        result = results[0]
        assert result.ranking_score is not None
        assert result.popularity_score is not None
        assert result.difficulty_score is not None
        assert 0.0 <= result.ranking_score <= 1.0
        assert 0.0 <= result.popularity_score <= 1.0
        assert 0.0 <= result.difficulty_score <= 1.0


class TestCachedKeywordScoringService:
    """キャッシュ機能付きキーワードスコアリングサービスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.service = CachedKeywordScoringService()

    def test_hash_keywords(self):
        """キーワードハッシュ生成テスト"""
        keywords = [
            KeywordData(keyword="test1", ranking=1, popularity=50.0, difficulty=30.0),
            KeywordData(keyword="test2", ranking=2, popularity=60.0, difficulty=40.0),
        ]

        hash1 = self.service._hash_keywords(keywords)
        hash2 = self.service._hash_keywords(keywords)

        # 同じキーワードリストは同じハッシュになる
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5ハッシュの長さ

    def test_hash_keywords_different_order(self):
        """異なる順序のキーワードハッシュテスト"""
        keywords1 = [
            KeywordData(keyword="test1", ranking=1, popularity=50.0, difficulty=30.0),
            KeywordData(keyword="test2", ranking=2, popularity=60.0, difficulty=40.0),
        ]
        keywords2 = [
            KeywordData(keyword="test2", ranking=2, popularity=60.0, difficulty=40.0),
            KeywordData(keyword="test1", ranking=1, popularity=50.0, difficulty=30.0),
        ]

        hash1 = self.service._hash_keywords(keywords1)
        hash2 = self.service._hash_keywords(keywords2)

        # 現在の実装では順序が異なるとハッシュも異なる
        # これは期待される動作（順序が重要）
        assert hash1 != hash2

    def test_score_keywords_cached(self):
        """キャッシュ機能付きスコアリングテスト"""
        keywords = [
            KeywordData(keyword="test1", ranking=1, popularity=50.0, difficulty=30.0),
            KeywordData(keyword="test2", ranking=2, popularity=60.0, difficulty=40.0),
        ]

        # 1回目のスコアリング
        results1 = self.service.score_keywords(keywords)

        # 2回目のスコアリング（キャッシュが使用される）
        results2 = self.service.score_keywords(keywords)

        # 結果が同じであることを確認
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1.keyword_data.keyword == r2.keyword_data.keyword
            assert abs(r1.composite_score - r2.composite_score) < 0.001

    def test_get_cache_key(self):
        """キャッシュキー生成テスト"""
        cache_key1 = self.service._get_cache_key("test_hash_1")
        cache_key2 = self.service._get_cache_key("test_hash_1")
        cache_key3 = self.service._get_cache_key("test_hash_2")

        # 同じハッシュは同じキャッシュキーになる
        assert cache_key1 == cache_key2
        # 異なるハッシュは異なるキャッシュキーになる
        assert cache_key1 != cache_key3


class TestScoringResultModel:
    """スコアリング結果モデルのテスト"""

    def test_scoring_result_model_valid(self):
        """正常なスコアリング結果モデルのテスト"""
        keyword_data = KeywordData(
            keyword="test", ranking=1, popularity=50.0, difficulty=30.0
        )

        scoring_result = PydanticScoringResult(
            keyword_data=keyword_data,
            composite_score=0.8,
            ranking_score=0.9,
            popularity_score=0.7,
            difficulty_score=0.6,
        )

        assert scoring_result.keyword_data == keyword_data
        assert scoring_result.composite_score == 0.8
        assert scoring_result.ranking_score == 0.9
        assert scoring_result.popularity_score == 0.7
        assert scoring_result.difficulty_score == 0.6

    def test_scoring_result_model_with_optional_scores(self):
        """オプションスコアなしのスコアリング結果モデルのテスト"""
        keyword_data = KeywordData(
            keyword="test", ranking=1, popularity=50.0, difficulty=30.0
        )

        scoring_result = PydanticScoringResult(
            keyword_data=keyword_data, composite_score=0.8
        )

        assert scoring_result.keyword_data == keyword_data
        assert scoring_result.composite_score == 0.8
        assert scoring_result.ranking_score is None
        assert scoring_result.popularity_score is None
        assert scoring_result.difficulty_score is None


class TestScoringResultsModel:
    """スコアリング結果リストモデルのテスト"""

    def test_scoring_results_model_valid(self):
        """正常なスコアリング結果リストモデルのテスト"""
        keyword_data1 = KeywordData(
            keyword="test1", ranking=1, popularity=50.0, difficulty=30.0
        )
        keyword_data2 = KeywordData(
            keyword="test2", ranking=2, popularity=60.0, difficulty=40.0
        )

        result1 = PydanticScoringResult(
            keyword_data=keyword_data1,
            composite_score=0.8,
            ranking_score=0.9,
            popularity_score=0.7,
            difficulty_score=0.6,
        )
        result2 = PydanticScoringResult(
            keyword_data=keyword_data2,
            composite_score=0.7,
            ranking_score=0.8,
            popularity_score=0.6,
            difficulty_score=0.5,
        )

        scoring_results = ScoringResults(
            results=[result1, result2], total_count=2, average_score=0.75
        )

        assert len(scoring_results.results) == 2
        assert scoring_results.total_count == 2
        assert scoring_results.average_score == 0.75
