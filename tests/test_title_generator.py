"""
タイトル生成機能のテスト
"""

from unittest.mock import Mock, patch

import pytest

from app.services.title_generator import (
    MultilingualTitleProcessor,
    TitleGenerationService,
    TitleGenerator,
)
from app.utils.exceptions import TextGenerationError


class TestTitleGenerator:
    """タイトル生成クラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.generator = TitleGenerator()

    def test_generate_title_success(self):
        """タイトル生成の成功テスト"""
        primary_keyword = "モバイルゲーム"
        app_base_name = "MyApp"
        result = self.generator.generate_title(primary_keyword, app_base_name, "ja")

        assert result is not None
        assert len(result) <= 30
        assert "モバイルゲーム" in result
        assert "MyApp" in result
        assert " - " in result

    def test_generate_title_english(self):
        """英語でのタイトル生成テスト"""
        primary_keyword = "mobile game"
        app_base_name = "MyApp"
        result = self.generator.generate_title(primary_keyword, app_base_name, "en")

        assert result is not None
        assert len(result) <= 30
        assert "Mobile Game" in result
        assert "Myapp" in result  # タイトルケース変換により"Myapp"になる
        assert " - " in result

    def test_generate_title_long_app_name(self):
        """長いアプリ名のタイトル生成テスト"""
        primary_keyword = "ゲーム"
        app_base_name = "非常に長いアプリケーション名です"
        result = self.generator.generate_title(primary_keyword, app_base_name, "ja")

        assert result is not None
        assert len(result) <= 30
        assert "ゲーム" in result

    def test_validate_inputs_success(self):
        """入力データ検証の成功テスト"""
        assert self.generator._validate_inputs("ゲーム", "MyApp") is True

    def test_validate_inputs_empty_keyword(self):
        """空のキーワードのテスト"""
        with pytest.raises(TextGenerationError, match="主要キーワードが空です"):
            self.generator._validate_inputs("", "MyApp")

    def test_validate_inputs_empty_app_name(self):
        """空のアプリ名のテスト"""
        with pytest.raises(TextGenerationError, match="アプリ基本名が空です"):
            self.generator._validate_inputs("ゲーム", "")

    def test_validate_inputs_too_long_keyword(self):
        """長すぎるキーワードのテスト"""
        long_keyword = "a" * 31
        with pytest.raises(TextGenerationError, match="主要キーワードが長すぎます"):
            self.generator._validate_inputs(long_keyword, "MyApp")

    def test_process_primary_keyword_japanese(self):
        """日本語キーワード処理のテスト"""
        keyword = "　モバイルゲーム　"  # 前後に空白
        result = self.generator._process_primary_keyword(keyword, "ja")

        assert result == "モバイルゲーム"
        assert len(result) <= 30

    def test_process_primary_keyword_english(self):
        """英語キーワード処理のテスト"""
        keyword = "  mobile game  "  # 前後に空白
        result = self.generator._process_primary_keyword(keyword, "en")

        assert result == "Mobile Game"

    def test_process_app_name_japanese(self):
        """日本語アプリ名処理のテスト"""
        app_name = "　マイアプリ　"  # 前後に空白
        result = self.generator._process_app_name(app_name, "ja")

        assert result == "マイアプリ"

    def test_process_app_name_english(self):
        """英語アプリ名処理のテスト"""
        app_name = "  my app  "  # 前後に空白
        result = self.generator._process_app_name(app_name, "en")

        assert result == "My App"

    def test_convert_fullwidth_to_halfwidth(self):
        """全角文字変換のテスト"""
        fullwidth_text = "１２３ＡＢＣａｂｃ"
        result = self.generator._convert_fullwidth_to_halfwidth(fullwidth_text)

        assert result == "123ABCabc"

    def test_normalize_english_keyword(self):
        """英語キーワード正規化のテスト"""
        keyword = "MOBILE GAME"
        result = self.generator._normalize_english_keyword(keyword)

        assert result == "Mobile Game"

    def test_to_title_case(self):
        """タイトルケース変換のテスト"""
        text = "my app name"
        result = self.generator._to_title_case(text)

        assert result == "My App Name"

    def test_remove_special_chars(self):
        """特殊文字除去のテスト"""
        text = "ゲーム<アプリ>名"
        result = self.generator._remove_special_chars(text)

        assert result == "ゲームアプリ名"

    def test_truncate_app_name(self):
        """アプリ名切り詰めのテスト"""
        long_app_name = "非常に長いアプリケーション名です"
        result = self.generator._truncate_app_name(long_app_name, 10)

        assert len(result) <= 10

    def test_truncate_app_name_with_space(self):
        """スペースを含むアプリ名の切り詰めテスト"""
        app_name_with_space = "mobile game adventure"
        result = self.generator._truncate_app_name(app_name_with_space, 10)

        assert len(result) <= 10
        # 10文字以内で切り詰められるため、"mobile"のみになる可能性がある
        assert result in ["mobile", "mobile game"]

    def test_get_separator(self):
        """区切り文字取得のテスト"""
        ja_separator = self.generator._get_separator("ja")
        en_separator = self.generator._get_separator("en")

        assert ja_separator == " - "
        assert en_separator == " - "

    def test_build_title_normal(self):
        """通常のタイトル構築テスト"""
        keyword = "ゲーム"
        app_name = "MyApp"
        separator = " - "
        result = self.generator._build_title(keyword, separator, app_name)

        assert result == "ゲーム - MyApp"
        assert len(result) <= 30

    def test_build_title_too_long(self):
        """長すぎるタイトルの構築テスト"""
        keyword = "非常に長いキーワード"
        app_name = "非常に長いアプリ名"
        separator = " - "
        result = self.generator._build_title(keyword, separator, app_name)

        assert len(result) <= 30

    def test_validate_title_success(self):
        """タイトル検証の成功テスト"""
        valid_title = "ゲーム - MyApp"
        assert self.generator._validate_title(valid_title) is True

    def test_validate_title_empty(self):
        """空のタイトルのテスト"""
        with pytest.raises(TextGenerationError, match="タイトルが空です"):
            self.generator._validate_title("")

    def test_validate_title_too_long(self):
        """長すぎるタイトルのテスト"""
        long_title = "a" * 31
        with pytest.raises(TextGenerationError, match="タイトルが長すぎます"):
            self.generator._validate_title(long_title)

    def test_validate_title_forbidden_chars(self):
        """禁止文字が含まれるタイトルのテスト"""
        invalid_title = "ゲーム<MyApp>"
        with pytest.raises(TextGenerationError, match="禁止文字"):
            self.generator._validate_title(invalid_title)


class TestMultilingualTitleProcessor:
    """多言語対応タイトル処理クラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.processor = MultilingualTitleProcessor()

    def test_process_title_for_language_japanese(self):
        """日本語タイトル処理のテスト"""
        keyword = "モバイルゲーム"
        app_name = "マイアプリ"
        processed_keyword, processed_app_name = (
            self.processor.process_title_for_language(keyword, app_name, "ja")
        )

        assert len(processed_keyword) <= 12
        assert len(processed_app_name) <= 15

    def test_process_title_for_language_english(self):
        """英語タイトル処理のテスト"""
        keyword = "mobile game"
        app_name = "my app"
        processed_keyword, processed_app_name = (
            self.processor.process_title_for_language(keyword, app_name, "en")
        )

        assert len(processed_keyword) <= 15
        assert len(processed_app_name) <= 12
        assert processed_app_name == "My App"  # タイトルケース

    def test_process_keyword_for_language(self):
        """言語に応じたキーワード処理のテスト"""
        keyword = "非常に長いキーワードです"
        rules = self.processor.language_rules["ja"]
        result = self.processor._process_keyword_for_language(keyword, rules)

        assert len(result) <= rules["max_keyword_length"]

    def test_process_app_name_for_language(self):
        """言語に応じたアプリ名処理のテスト"""
        app_name = "非常に長いアプリ名です"
        rules = self.processor.language_rules["ja"]
        result = self.processor._process_app_name_for_language(app_name, rules)

        assert len(result) <= rules["max_app_name_length"]


class TestTitleGenerationService:
    """統合タイトル生成サービスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.service = TitleGenerationService()

    def test_generate_title_success(self):
        """タイトル生成の成功テスト"""
        primary_keyword = "モバイルゲーム"
        app_base_name = "MyApp"
        result = self.service.generate_title(primary_keyword, app_base_name, "ja")

        assert "title" in result
        assert "length" in result
        assert "primary_keyword" in result
        assert "app_base_name" in result
        assert "language" in result
        assert "generated_at" in result
        assert result["length"] <= 30

    def test_generate_title_empty_keyword(self):
        """空のキーワードのテスト"""
        with pytest.raises(
            TextGenerationError, match="主要キーワードまたはアプリ基本名が空です"
        ):
            self.service.generate_title("", "MyApp", "ja")

    def test_generate_title_empty_app_name(self):
        """空のアプリ名のテスト"""
        with pytest.raises(
            TextGenerationError, match="主要キーワードまたはアプリ基本名が空です"
        ):
            self.service.generate_title("ゲーム", "", "ja")

    def test_generate_title_english(self):
        """英語でのタイトル生成テスト"""
        primary_keyword = "mobile game"
        app_base_name = "MyApp"
        result = self.service.generate_title(primary_keyword, app_base_name, "en")

        assert result["language"] == "en"
        assert result["primary_keyword"] == "mobile game"
        assert result["app_base_name"] == "MyApp"
        assert result["length"] <= 30


class TestIntegration:
    """統合テスト"""

    def test_full_title_generation_workflow(self):
        """完全なタイトル生成ワークフローのテスト"""
        # タイトル生成をシミュレート
        primary_keyword = "モバイルゲーム"
        app_base_name = "マイアプリ"

        service = TitleGenerationService()
        result = service.generate_title(primary_keyword, app_base_name, "ja")

        # 結果の検証
        assert result["title"] is not None
        assert result["length"] <= 30
        assert result["primary_keyword"] == "モバイルゲーム"
        assert result["app_base_name"] == "マイアプリ"
        assert result["language"] == "ja"
        assert "generated_at" in result

        # タイトルの内容検証
        title = result["title"]
        assert "モバイルゲーム" in title
        assert "マイアプリ" in title
        assert " - " in title  # 区切り文字
        assert len(title.split(" - ")) == 2  # キーワードとアプリ名の2つ

    def test_title_template_compliance(self):
        """タイトルテンプレート準拠のテスト"""
        primary_keyword = "ゲーム"
        app_base_name = "MyApp"

        service = TitleGenerationService()
        result = service.generate_title(primary_keyword, app_base_name, "ja")

        title = result["title"]
        # 「{主要キーワード} - {アプリ基本名}」テンプレートに従っているかチェック
        parts = title.split(" - ")
        assert len(parts) == 2
        assert "ゲーム" in parts[0]
        assert "MyApp" in parts[1]
