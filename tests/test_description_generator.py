"""
概要生成サービスのテスト
"""

from unittest.mock import Mock, patch

import pytest

from app.services.description_generator import DescriptionGenerator
from app.services.gemini_generator import GeminiGenerator


class TestDescriptionGenerator:
    """概要生成クラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.mock_gemini = Mock(spec=GeminiGenerator)
        self.description_generator = DescriptionGenerator(self.mock_gemini)

        # テスト用のアプリ情報
        self.test_app_info = {
            "name": "テストアプリ",
            "features": ["機能1", "機能2", "機能3"],
            "target_audience": "一般ユーザー",
            "related_keywords": ["キーワード1", "キーワード2"],
        }
        self.test_main_keyword = "テストキーワード"

    def test_init(self):
        """初期化のテスト"""
        assert self.description_generator.gemini_generator == self.mock_gemini
        assert self.description_generator.max_length == 4000
        assert self.description_generator.min_keyword_count == 4
        assert self.description_generator.max_keyword_count == 7

    def test_prepare_prompt_ja(self):
        """日本語プロンプト準備のテスト"""
        prompt = self.description_generator._prepare_prompt(
            self.test_app_info, self.test_main_keyword, "ja"
        )

        assert "テストアプリ" in prompt
        assert "機能1, 機能2, 機能3" in prompt
        assert "テストキーワード" in prompt
        assert "一般ユーザー" in prompt
        assert "4000文字以内" in prompt

    def test_prepare_prompt_en(self):
        """英語プロンプト準備のテスト"""
        prompt = self.description_generator._prepare_prompt(
            self.test_app_info, self.test_main_keyword, "en"
        )

        assert "Within 4000 characters" in prompt
        assert "Naturally include main keyword" in prompt

    def test_check_keyword_density(self):
        """キーワード密度チェックのテスト"""
        text = "これはテストキーワードを含むテキストです。テストキーワードが複数回出現します。"
        count = self.description_generator._check_keyword_density(
            text, "テストキーワード"
        )
        assert count == 2

    def test_check_keyword_density_case_insensitive(self):
        """大文字小文字を区別しないキーワード密度チェックのテスト"""
        text = (
            "これはTESTキーワードを含むテキストです。testキーワードが複数回出現します。"
        )
        count = self.description_generator._check_keyword_density(
            text, "TESTキーワード"
        )
        assert count == 2

    def test_adjust_length_within_limit(self):
        """文字数制限内の調整テスト"""
        text = "短いテキスト"
        result = self.description_generator._adjust_length(text, 100)
        assert result == text

    def test_adjust_length_exceeds_limit(self):
        """文字数制限超過時の調整テスト"""
        long_text = "長いテキスト。" * 1000  # 4000文字を超える
        result = self.description_generator._adjust_length(long_text, 100)
        assert len(result) <= 100

    def test_validate_description_valid(self):
        """有効な概要の検証テスト"""
        valid_description = "テストキーワードを含む有効な概要です。これは2番目の文です。これは3番目の文です。これは4番目の文です。これは5番目の文です。テストキーワードが再度出現します。これは6番目の文です。テストキーワードが3回目に出現します。これは7番目の文です。テストキーワードが4回目に出現します。"
        result = self.description_generator._validate_description(
            valid_description, "テストキーワード"
        )
        assert result is True

    def test_validate_description_too_long(self):
        """長すぎる概要の検証テスト"""
        long_description = "長いテキスト。" * 1000  # 4000文字を超える
        result = self.description_generator._validate_description(
            long_description, "テストキーワード"
        )
        assert result is False

    def test_validate_description_too_short(self):
        """短すぎる概要の検証テスト"""
        short_description = "短い"
        result = self.description_generator._validate_description(
            short_description, "テストキーワード"
        )
        assert result is False

    def test_optimize_keyword_placement_optimal(self):
        """最適なキーワード配置のテスト"""
        text = "テストキーワードを含むテキストです。" * 5  # 5回出現
        result = self.description_generator._optimize_keyword_placement(
            text, "テストキーワード"
        )
        assert result == text  # 変更なし

    def test_optimize_keyword_placement_too_few(self):
        """キーワードが少ない場合の最適化テスト"""
        text = "テストキーワードを含むテキストです。これは別の文です。これは3番目の文です。これは4番目の文です。これは5番目の文です。これは6番目の文です。これは7番目の文です。これは8番目の文です。"
        result = self.description_generator._optimize_keyword_placement(
            text, "テストキーワード"
        )
        # キーワードが追加されることを確認
        count = self.description_generator._check_keyword_density(
            result, "テストキーワード"
        )
        assert count >= 3  # 最低3回は追加されることを確認

    def test_optimize_keyword_placement_too_many(self):
        """キーワードが多い場合の最適化テスト"""
        text = (
            "テストキーワードを含むテキストです。テストキーワードが多すぎます。" * 10
        )  # 20回出現
        result = self.description_generator._optimize_keyword_placement(
            text, "テストキーワード"
        )
        # キーワードが削減されることを確認
        count = self.description_generator._check_keyword_density(
            result, "テストキーワード"
        )
        assert count <= 7

    @patch("app.services.description_generator.logger")
    def test_generate_description_success(self, mock_logger):
        """概要生成成功のテスト"""
        mock_description = "テストキーワードを含む有効な概要です。" * 50
        self.mock_gemini.generate_description.return_value = mock_description

        result = self.description_generator.generate_description(
            self.test_app_info, self.test_main_keyword, "ja"
        )

        assert len(result) <= 4000
        assert "テストキーワード" in result
        self.mock_gemini.generate_description.assert_called_once()

    @patch("app.services.description_generator.logger")
    def test_generate_description_validation_failure_retry(self, mock_logger):
        """検証失敗時の再生成テスト"""
        # 最初の生成は失敗、2回目は成功
        invalid_description = "短い"
        valid_description = "テストキーワードを含む有効な概要です。" * 50

        self.mock_gemini.generate_description.side_effect = [
            invalid_description,
            valid_description,
        ]

        result = self.description_generator.generate_description(
            self.test_app_info, self.test_main_keyword, "ja"
        )

        assert len(result) <= 4000
        assert self.mock_gemini.generate_description.call_count == 2

    @patch("app.services.description_generator.logger")
    def test_generate_description_exception(self, mock_logger):
        """例外発生時のテスト"""
        self.mock_gemini.generate_description.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            self.description_generator.generate_description(
                self.test_app_info, self.test_main_keyword, "ja"
            )

    def test_add_keywords(self):
        """キーワード追加のテスト"""
        text = "これは最初の文です。これは2番目の文です。これは3番目の文です。これは4番目の文です。"
        result = self.description_generator._add_keywords(text, "テストキーワード", 2)

        count = self.description_generator._check_keyword_density(
            result, "テストキーワード"
        )
        assert count >= 1  # 最低1回は追加されることを確認

    def test_reduce_keywords(self):
        """キーワード削減のテスト"""
        text = "テストキーワードを含む文です。テストキーワードが多すぎます。" * 5
        result = self.description_generator._reduce_keywords(
            text, "テストキーワード", 3
        )

        original_count = self.description_generator._check_keyword_density(
            text, "テストキーワード"
        )
        result_count = self.description_generator._check_keyword_density(
            result, "テストキーワード"
        )
        assert result_count <= original_count - 3

    def test_is_safe_to_remove_safe(self):
        """安全な削除のテスト"""
        text = "これは長い文です。テストキーワードを含んでいます。"
        result = self.description_generator._is_safe_to_remove(text, 10, 20)
        assert result is True

    def test_is_safe_to_remove_unsafe(self):
        """安全でない削除のテスト"""
        text = "短い"
        result = self.description_generator._is_safe_to_remove(text, 0, 2)
        assert result is False

    def test_post_process_description(self):
        """後処理のテスト"""
        description = "テストキーワードを含む長いテキストです。" * 100
        result = self.description_generator._post_process_description(
            description, "テストキーワード"
        )

        assert len(result) <= 4000
        assert "テストキーワード" in result
