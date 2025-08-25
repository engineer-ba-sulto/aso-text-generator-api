"""
最新情報生成機能のテスト
"""

from unittest.mock import Mock, patch

import pytest

from app.services.whats_new_generator import (
    MultilingualWhatsNewProcessor,
    WhatsNewGenerationService,
    WhatsNewGenerator,
)
from app.utils.exceptions import TextGenerationError


class TestWhatsNewGenerator:
    """最新情報生成クラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.generator = WhatsNewGenerator()
        self.sample_features = ["新しいUIデザイン", "パフォーマンス向上", "バグ修正"]

    def test_generate_whats_new_success(self):
        """最新情報生成の成功テスト"""
        primary_keyword = "モバイルゲーム"
        result = self.generator.generate_whats_new(
            primary_keyword, self.sample_features, "ja"
        )

        assert result is not None
        assert len(result) <= 4000
        assert "モバイルゲーム" in result
        assert "新しいUIデザイン" in result

    def test_generate_whats_new_english(self):
        """英語での最新情報生成テスト"""
        primary_keyword = "mobile game"
        english_features = ["New UI design", "Performance improvements", "Bug fixes"]
        result = self.generator.generate_whats_new(
            primary_keyword, english_features, "en"
        )

        assert result is not None
        assert len(result) <= 4000
        assert "mobile game" in result
        assert "New UI design" in result

    def test_validate_inputs_success(self):
        """入力データ検証の成功テスト"""
        assert self.generator._validate_inputs("ゲーム", self.sample_features) is True

    def test_validate_inputs_empty_keyword(self):
        """空のキーワードのテスト"""
        with pytest.raises(TextGenerationError, match="主要キーワードが空です"):
            self.generator._validate_inputs("", self.sample_features)

    def test_validate_inputs_empty_features(self):
        """空の特徴リストのテスト"""
        with pytest.raises(TextGenerationError, match="アプリの特徴リストが空です"):
            self.generator._validate_inputs("ゲーム", [])

    def test_validate_inputs_too_long_keyword(self):
        """長すぎるキーワードのテスト"""
        long_keyword = "a" * 51
        with pytest.raises(TextGenerationError, match="主要キーワードが長すぎます"):
            self.generator._validate_inputs(long_keyword, self.sample_features)

    def test_get_template_japanese(self):
        """日本語テンプレート取得のテスト"""
        template = self.generator._get_template("ja")
        assert template is not None
        assert "{keyword_placeholder}" in template

    def test_get_template_english(self):
        """英語テンプレート取得のテスト"""
        template = self.generator._get_template("en")
        assert template is not None
        assert "{keyword_placeholder}" in template

    def test_get_template_unsupported_language(self):
        """サポートされていない言語のテスト"""
        with pytest.raises(TextGenerationError, match="サポートされていない言語です"):
            self.generator._get_template("fr")

    def test_integrate_keyword(self):
        """キーワード統合のテスト"""
        template = "This is a {keyword_placeholder} template."
        keyword = "test"
        result = self.generator._integrate_keyword(template, keyword, "en")

        assert keyword in result
        assert "{keyword_placeholder}" not in result

    def test_adjust_keyword_occurrences_add(self):
        """キーワード出現回数追加のテスト"""
        content = "This is a test. Test is good."
        keyword = "test"
        result = self.generator._adjust_keyword_occurrences(content, keyword, "en")

        # 最小出現回数（4回）以上になることを確認
        assert result.count(keyword) >= 4

    def test_adjust_keyword_occurrences_reduce(self):
        """キーワード出現回数削減のテスト"""
        content = "test. test. test. test. test. test. test. test. test. test."
        keyword = "test"
        result = self.generator._adjust_keyword_occurrences(content, keyword, "en")

        # 最大出現回数（7回）以下になることを確認
        assert result.count(keyword) <= 7

    def test_create_sentence_with_keyword_japanese(self):
        """日本語キーワード文作成のテスト"""
        keyword = "ゲーム"
        result = self.generator._create_sentence_with_keyword(keyword, "ja")

        assert keyword in result
        assert result.endswith("。")

    def test_create_sentence_with_keyword_english(self):
        """英語キーワード文作成のテスト"""
        keyword = "game"
        result = self.generator._create_sentence_with_keyword(keyword, "en")

        assert keyword in result
        assert result.endswith(".")

    def test_get_sentences_japanese(self):
        """日本語文分割のテスト"""
        content = "これは文です。これは別の文です。"
        sentences = self.generator._get_sentences(content, "ja")

        assert len(sentences) == 2
        assert "これは文です" in sentences[0]
        assert "これは別の文です" in sentences[1]

    def test_get_sentences_english(self):
        """英語文分割のテスト"""
        content = "This is a sentence. This is another sentence."
        sentences = self.generator._get_sentences(content, "en")

        assert len(sentences) == 2
        assert "This is a sentence" in sentences[0]
        assert "This is another sentence" in sentences[1]

    def test_integrate_features(self):
        """特徴統合のテスト"""
        content = "【主な変更点】\n• 既存の項目"
        features = ["新機能1", "新機能2"]
        result = self.generator._integrate_features(content, features, "ja")

        assert "新機能1" in result
        assert "新機能2" in result

    def test_format_features_japanese(self):
        """日本語特徴フォーマットのテスト"""
        features = ["機能1", "機能2"]
        result = self.generator._format_features(features, "ja")

        assert "• 機能1" in result
        assert "• 機能2" in result

    def test_format_features_english(self):
        """英語特徴フォーマットのテスト"""
        features = ["Feature 1", "Feature 2"]
        result = self.generator._format_features(features, "en")

        assert "• Feature 1" in result
        assert "• Feature 2" in result

    def test_optimize_length(self):
        """文字数最適化のテスト"""
        long_content = "a" * 5000
        result = self.generator._optimize_length(long_content)

        assert len(result) <= 4000

    def test_validate_content_success(self):
        """コンテンツ検証の成功テスト"""
        content = "これはテストです。テストキーワードが含まれています。テスト機能を追加しました。テストの改善を行いました。"
        keyword = "テスト"
        assert self.generator._validate_content(content, keyword) is True

    def test_validate_content_empty(self):
        """空のコンテンツのテスト"""
        with pytest.raises(TextGenerationError, match="最新情報が空です"):
            self.generator._validate_content("", "テスト")

    def test_validate_content_too_long(self):
        """長すぎるコンテンツのテスト"""
        long_content = "a" * 4001
        with pytest.raises(TextGenerationError, match="最新情報が長すぎます"):
            self.generator._validate_content(long_content, "テスト")

    def test_validate_content_insufficient_keywords(self):
        """キーワード不足のテスト"""
        content = "これはテストです。"
        keyword = "テスト"
        with pytest.raises(
            TextGenerationError, match="キーワードの出現回数が少なすぎます"
        ):
            self.generator._validate_content(content, keyword)

    def test_validate_content_too_many_keywords(self):
        """キーワード過多のテスト"""
        content = "テスト " * 10  # 10回出現
        keyword = "テスト"
        with pytest.raises(
            TextGenerationError, match="キーワードの出現回数が多すぎます"
        ):
            self.generator._validate_content(content, keyword)


class TestMultilingualWhatsNewProcessor:
    """多言語対応最新情報処理クラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.processor = MultilingualWhatsNewProcessor()

    def test_process_whats_new_for_language_japanese(self):
        """日本語最新情報処理のテスト"""
        content = "これは長い文です。これは別の長い文です。"
        result = self.processor.process_whats_new_for_language(content, "ja")

        assert result is not None
        assert len(result) > 0

    def test_process_whats_new_for_language_english(self):
        """英語最新情報処理のテスト"""
        content = "This is a long sentence. This is another long sentence."
        result = self.processor.process_whats_new_for_language(content, "en")

        assert result is not None
        assert len(result) > 0

    def test_adjust_sentence_lengths(self):
        """文の長さ調整のテスト"""
        content = "短い文。"
        rules = self.processor.language_rules["ja"]
        result = self.processor._adjust_sentence_lengths(content, rules)

        assert result is not None

    def test_split_sentences(self):
        """文分割のテスト"""
        content = "文1。文2。文3。"
        endings = ["。"]
        sentences = self.processor._split_sentences(content, endings)

        assert len(sentences) == 3

    def test_split_long_sentence(self):
        """長い文分割のテスト"""
        long_sentence = "これは非常に長い文で、カンマで区切られています。"
        rules = self.processor.language_rules["ja"]
        result = self.processor._split_long_sentence(long_sentence, rules)

        assert len(result) >= 1

    def test_normalize_format(self):
        """フォーマット統一のテスト"""
        content = "• 項目1\n• 項目2"
        rules = self.processor.language_rules["ja"]
        result = self.processor._normalize_format(content, rules)

        assert "• 項目1" in result
        assert "• 項目2" in result


class TestWhatsNewGenerationService:
    """統合最新情報生成サービスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.service = WhatsNewGenerationService()

    def test_generate_whats_new_success(self):
        """最新情報生成の成功テスト"""
        primary_keyword = "モバイルゲーム"
        app_features = ["新機能", "改善点"]
        result = self.service.generate_whats_new(primary_keyword, app_features, "ja")

        assert "whats_new" in result
        assert "length" in result
        assert "primary_keyword" in result
        assert "keyword_occurrences" in result
        assert "language" in result
        assert "generated_at" in result
        assert result["length"] <= 4000

    def test_generate_whats_new_empty_keyword(self):
        """空のキーワードのテスト"""
        with pytest.raises(
            TextGenerationError, match="主要キーワードまたはアプリの特徴が空です"
        ):
            self.service.generate_whats_new("", ["特徴"], "ja")

    def test_generate_whats_new_empty_features(self):
        """空の特徴リストのテスト"""
        with pytest.raises(
            TextGenerationError, match="主要キーワードまたはアプリの特徴が空です"
        ):
            self.service.generate_whats_new("キーワード", [], "ja")

    def test_generate_whats_new_english(self):
        """英語での最新情報生成テスト"""
        primary_keyword = "mobile game"
        app_features = ["new feature", "improvement"]
        result = self.service.generate_whats_new(primary_keyword, app_features, "en")

        assert result["language"] == "en"
        assert result["primary_keyword"] == "mobile game"
        assert result["length"] <= 4000


class TestIntegration:
    """統合テスト"""

    def test_full_whats_new_generation_workflow(self):
        """完全な最新情報生成ワークフローのテスト"""
        # 最新情報生成をシミュレート
        primary_keyword = "モバイルゲーム"
        app_features = [
            "新しいUIデザイン",
            "パフォーマンス向上",
            "バグ修正",
            "新機能追加",
        ]

        service = WhatsNewGenerationService()
        result = service.generate_whats_new(primary_keyword, app_features, "ja")

        # 結果の検証
        assert result["whats_new"] is not None
        assert result["length"] <= 4000
        assert result["primary_keyword"] == "モバイルゲーム"
        assert result["language"] == "ja"
        assert "generated_at" in result

        # 最新情報の内容検証
        whats_new = result["whats_new"]
        assert "モバイルゲーム" in whats_new
        assert "新しいUIデザイン" in whats_new
        assert "【新機能・改善点】" in whats_new
        assert "【主な変更点】" in whats_new
        assert "【詳細】" in whats_new
        assert "【今後の予定】" in whats_new

        # キーワード出現回数の検証
        keyword_count = result["keyword_occurrences"]
        assert 4 <= keyword_count <= 7

    def test_template_structure_compliance(self):
        """テンプレート構造準拠のテスト"""
        primary_keyword = "ゲーム"
        app_features = ["機能1", "機能2"]

        service = WhatsNewGenerationService()
        result = service.generate_whats_new(primary_keyword, app_features, "ja")

        whats_new = result["whats_new"]
        # テンプレート構造に従っているかチェック
        assert "【新機能・改善点】" in whats_new
        assert "【主な変更点】" in whats_new
        assert "【詳細】" in whats_new
        assert "【今後の予定】" in whats_new
        assert "ご利用いただき、ありがとうございます。" in whats_new
