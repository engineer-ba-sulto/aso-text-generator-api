"""
キーワードフィールド生成機能のテスト
"""

from unittest.mock import Mock, patch

import pytest

from app.services.keyword_field_generator import (
    KeywordFieldGenerationService,
    KeywordFieldGenerator,
    MultilingualKeywordProcessor,
)
from app.utils.exceptions import TextGenerationError


class TestKeywordFieldGenerator:
    """キーワードフィールド生成クラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.generator = KeywordFieldGenerator()
        self.sample_candidates = [
            {"keyword": "ゲーム", "score": 0.9},
            {"keyword": "アクション", "score": 0.8},
            {"keyword": "RPG", "score": 0.7},
            {"keyword": "アドベンチャー", "score": 0.6},
            {"keyword": "パズル", "score": 0.5},
        ]

    def test_generate_keyword_field_success(self):
        """キーワードフィールド生成の成功テスト"""
        primary_keyword = "モバイルゲーム"
        result = self.generator.generate_keyword_field(
            primary_keyword, self.sample_candidates, "ja"
        )

        assert result is not None
        assert len(result) <= 100
        assert "モバイルゲーム" in result
        assert "ゲーム" in result

    def test_generate_keyword_field_english(self):
        """英語でのキーワードフィールド生成テスト"""
        primary_keyword = "mobile game"
        english_candidates = [
            {"keyword": "action", "score": 0.9},
            {"keyword": "rpg", "score": 0.8},
            {"keyword": "adventure", "score": 0.7},
        ]

        result = self.generator.generate_keyword_field(
            primary_keyword, english_candidates, "en"
        )

        assert result is not None
        assert len(result) <= 100
        assert "mobile game" in result
        assert ", " in result  # 英語の区切り文字

    def test_remove_duplicates(self):
        """重複除去のテスト"""
        keywords = ["ゲーム", "ゲーム", "アクション", "action", "Action"]
        unique = self.generator._remove_duplicates(keywords)

        # 正規化後の重複は除去される
        assert len(unique) < len(keywords)
        assert "ゲーム" in unique
        assert "アクション" in unique

    def test_sort_by_score(self):
        """スコア順ソートのテスト"""
        keywords = ["ゲーム", "RPG", "アクション"]
        sorted_keywords = self.generator._sort_by_score(
            keywords, self.sample_candidates
        )

        # スコア順でソートされていることを確認
        assert len(sorted_keywords) == 3
        # 主要キーワード（ゲーム）が最初に来る（スコア1.0が設定される）
        assert sorted_keywords[0] == "ゲーム"

    def test_optimize_length(self):
        """文字数最適化のテスト"""
        long_keywords = ["非常に長いキーワード" * 10] * 5
        optimized = self.generator._optimize_length(long_keywords)

        # 100文字以内に収まる
        result = "、".join(optimized)
        assert len(result) <= 100

    def test_validate_keyword_field_success(self):
        """キーワードフィールド検証の成功テスト"""
        valid_field = "ゲーム、アクション、RPG"
        assert self.generator._validate_keyword_field(valid_field) is True

    def test_validate_keyword_field_too_long(self):
        """キーワードフィールドが長すぎる場合のテスト"""
        long_field = "a" * 101
        with pytest.raises(TextGenerationError, match="長すぎます"):
            self.generator._validate_keyword_field(long_field)

    def test_validate_keyword_field_forbidden_chars(self):
        """禁止文字が含まれる場合のテスト"""
        invalid_field = "ゲーム<アクション>RPG"
        with pytest.raises(TextGenerationError, match="禁止文字"):
            self.generator._validate_keyword_field(invalid_field)

    def test_empty_keywords(self):
        """空のキーワードリストのテスト"""
        with pytest.raises(TextGenerationError, match="キーワードが空です"):
            self.generator._build_keyword_field([], "ja")


class TestMultilingualKeywordProcessor:
    """多言語対応キーワード処理クラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.processor = MultilingualKeywordProcessor()

    def test_process_keywords_japanese(self):
        """日本語キーワード処理のテスト"""
        keywords = ["ゲーム", "アクション", "RPG", "アドベンチャー"]
        processed = self.processor.process_keywords_for_language(keywords, "ja")

        assert len(processed) <= 8  # 日本語の最大キーワード数
        assert all(len(k) >= 2 for k in processed)  # 最小長チェック

    def test_process_keywords_english(self):
        """英語キーワード処理のテスト"""
        keywords = ["game", "action", "rpg", "adventure"]
        processed = self.processor.process_keywords_for_language(keywords, "en")

        assert len(processed) <= 10  # 英語の最大キーワード数
        assert all(len(k) >= 3 for k in processed)  # 最小長チェック

    def test_truncate_keyword(self):
        """キーワード切り詰めのテスト"""
        long_keyword = "非常に長いキーワードです"
        truncated = self.processor._truncate_keyword(long_keyword, 10)

        assert len(truncated) <= 10

    def test_truncate_keyword_with_space(self):
        """スペースを含むキーワードの切り詰めテスト"""
        keyword_with_space = "mobile game adventure"
        truncated = self.processor._truncate_keyword(keyword_with_space, 10)

        assert len(truncated) <= 10
        # 10文字以内で切り詰められるため、"mobile"のみになる可能性がある
        assert truncated in ["mobile", "mobile game"]


class TestKeywordFieldGenerationService:
    """統合キーワードフィールド生成サービスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.service = KeywordFieldGenerationService()

    def test_generate_keyword_field_success(self):
        """キーワードフィールド生成の成功テスト"""
        selection_result = {
            "primary_keyword": "モバイルゲーム",
            "candidates": [
                {"keyword": "ゲーム", "score": 0.9},
                {"keyword": "アクション", "score": 0.8},
                {"keyword": "RPG", "score": 0.7},
            ],
        }

        result = self.service.generate_keyword_field(selection_result, "ja")

        assert "keyword_field" in result
        assert "length" in result
        assert "primary_keyword" in result
        assert "language" in result
        assert "generated_at" in result
        assert result["length"] <= 100

    def test_generate_keyword_field_empty_selection(self):
        """空の選定結果のテスト"""
        with pytest.raises(TextGenerationError, match="キーワード選定結果が空です"):
            self.service.generate_keyword_field({}, "ja")

    def test_generate_keyword_field_no_primary_keyword(self):
        """主要キーワードがない場合のテスト"""
        selection_result = {"candidates": [{"keyword": "ゲーム", "score": 0.9}]}

        with pytest.raises(
            TextGenerationError, match="主要キーワードが設定されていません"
        ):
            self.service.generate_keyword_field(selection_result, "ja")

    def test_generate_keyword_field_english(self):
        """英語でのキーワードフィールド生成テスト"""
        selection_result = {
            "primary_keyword": "mobile game",
            "candidates": [
                {"keyword": "action", "score": 0.9},
                {"keyword": "rpg", "score": 0.8},
            ],
        }

        result = self.service.generate_keyword_field(selection_result, "en")

        assert result["language"] == "en"
        assert result["primary_keyword"] == "mobile game"
        assert result["length"] <= 100


class TestIntegration:
    """統合テスト"""

    def test_full_keyword_field_generation_workflow(self):
        """完全なキーワードフィールド生成ワークフローのテスト"""
        # キーワード選定結果をシミュレート
        selection_result = {
            "primary_keyword": "モバイルゲーム",
            "candidates": [
                {"keyword": "ゲーム", "score": 0.95},
                {"keyword": "アクション", "score": 0.85},
                {"keyword": "RPG", "score": 0.75},
                {"keyword": "アドベンチャー", "score": 0.65},
                {"keyword": "パズル", "score": 0.55},
                {"keyword": "シミュレーション", "score": 0.45},
                {"keyword": "ストラテジー", "score": 0.35},
                {"keyword": "レーシング", "score": 0.25},
                {"keyword": "スポーツ", "score": 0.15},
                {"keyword": "音楽", "score": 0.05},
            ],
        }

        service = KeywordFieldGenerationService()
        result = service.generate_keyword_field(selection_result, "ja")

        # 結果の検証
        assert result["keyword_field"] is not None
        assert result["length"] <= 100
        assert result["primary_keyword"] == "モバイルゲーム"
        assert result["language"] == "ja"
        assert "generated_at" in result

        # キーワードフィールドの内容検証
        keyword_field = result["keyword_field"]
        assert "モバイルゲーム" in keyword_field
        assert "、" in keyword_field  # 日本語の区切り文字
        assert len(keyword_field.split("、")) <= 10  # 最大キーワード数
