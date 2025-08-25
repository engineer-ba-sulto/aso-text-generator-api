"""
サブタイトル生成サービスのテスト
"""

import pytest
from unittest.mock import Mock, patch

# 設定ファイルの読み込みをモック化
with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key', 'GEMINI_API_KEY': 'test_key'}):
    from app.services.subtitle_generator import SubtitleGenerator
    from app.services.gemini_generator import GeminiGenerator


class TestSubtitleGenerator:
    """SubtitleGeneratorクラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.mock_gemini = Mock(spec=GeminiGenerator)
        self.subtitle_generator = SubtitleGenerator(self.mock_gemini)
        self.test_app_info = {
            "name": "テストアプリ",
            "features": "便利な機能、使いやすいインターフェース",
            "target_audience": "一般ユーザー"
        }

    def test_init(self):
        """初期化テスト"""
        assert self.subtitle_generator.gemini_generator == self.mock_gemini
        assert self.subtitle_generator.max_length == 30

    @patch('app.services.subtitle_generator.PromptManager')
    def test_prepare_prompt(self, mock_prompt_manager):
        """プロンプト準備テスト"""
        mock_prompt_manager.get_subtitle_prompt.return_value = "テストプロンプト"
        
        prompt = self.subtitle_generator._prepare_prompt(
            self.test_app_info, "テスト", "ja"
        )
        
        mock_prompt_manager.get_subtitle_prompt.assert_called_once_with(
            language="ja",
            app_name="テストアプリ",
            app_features="便利な機能、使いやすいインターフェース",
            main_keyword="テスト",
            target_audience="一般ユーザー"
        )
        assert prompt == "テストプロンプト"

    def test_validate_subtitle_valid(self):
        """有効なサブタイトルの検証テスト"""
        subtitle = "便利なアプリ"
        result = self.subtitle_generator._validate_subtitle(subtitle, "テスト")
        assert result is True

    def test_validate_subtitle_too_long(self):
        """長すぎるサブタイトルの検証テスト"""
        subtitle = "これは30文字を超える非常に長いサブタイトルです。実際に30文字を超えています。"
        result = self.subtitle_generator._validate_subtitle(subtitle, "テスト")
        assert result is False

    def test_validate_subtitle_contains_keyword(self):
        """キーワードを含むサブタイトルの検証テスト"""
        subtitle = "テストアプリ"
        result = self.subtitle_generator._validate_subtitle(subtitle, "テスト")
        assert result is False

    def test_validate_subtitle_empty(self):
        """空のサブタイトルの検証テスト"""
        subtitle = ""
        result = self.subtitle_generator._validate_subtitle(subtitle, "テスト")
        assert result is False

    def test_validate_subtitle_inappropriate_content(self):
        """不適切なコンテンツを含むサブタイトルの検証テスト"""
        subtitle = "不適切なアプリ"
        result = self.subtitle_generator._validate_subtitle(subtitle, "テスト")
        assert result is False

    def test_adjust_length_within_limit(self):
        """制限内の文字数調整テスト"""
        subtitle = "短いタイトル"
        result = self.subtitle_generator._adjust_length(subtitle, 30)
        assert result == "短いタイトル"

    def test_adjust_length_exceeds_limit(self):
        """制限超過の文字数調整テスト"""
        subtitle = "これは30文字を超える非常に長いサブタイトルです"
        result = self.subtitle_generator._adjust_length(subtitle, 30)
        assert len(result) <= 30

    def test_adjust_length_with_period(self):
        """句読点での文字数調整テスト"""
        subtitle = "これは長いタイトルです。追加の説明。"
        result = self.subtitle_generator._adjust_length(subtitle, 15)
        assert result == "これは長いタイトルです。"

    def test_filter_keywords(self):
        """キーワードフィルタリングテスト"""
        text = "テストアプリは便利です"
        result = self.subtitle_generator._filter_keywords(text, ["テスト"])
        assert "テスト" not in result

    def test_filter_keywords_case_insensitive(self):
        """大文字小文字を区別しないキーワードフィルタリングテスト"""
        text = "TestApp is useful"
        result = self.subtitle_generator._filter_keywords(text, ["test"])
        assert "test" not in result.lower()

    def test_filter_keywords_multiple(self):
        """複数キーワードのフィルタリングテスト"""
        text = "テストアプリとサンプルアプリ"
        result = self.subtitle_generator._filter_keywords(text, ["テスト", "サンプル"])
        assert "テスト" not in result
        assert "サンプル" not in result

    def test_contains_keyword_true(self):
        """キーワード含有一致テスト"""
        text = "テストアプリ"
        result = self.subtitle_generator._contains_keyword(text, "テスト")
        assert result is True

    def test_contains_keyword_false(self):
        """キーワード非含有テスト"""
        text = "便利なアプリ"
        result = self.subtitle_generator._contains_keyword(text, "テスト")
        assert result is False

    def test_contains_keyword_case_insensitive(self):
        """大文字小文字を区別しないキーワード検索テスト"""
        text = "TestApp"
        result = self.subtitle_generator._contains_keyword(text, "test")
        assert result is True

    def test_clean_text(self):
        """テキストクリーニングテスト"""
        text = "  テストアプリ。  "
        result = self.subtitle_generator._clean_text(text)
        assert result == "テストアプリ"

    def test_clean_text_multiple_spaces(self):
        """複数空白のクリーニングテスト"""
        text = "テスト  アプリ"
        result = self.subtitle_generator._clean_text(text)
        assert result == "テスト アプリ"

    def test_clean_text_punctuation(self):
        """句読点のクリーニングテスト"""
        text = "。テストアプリ、"
        result = self.subtitle_generator._clean_text(text)
        assert result == "テストアプリ"

    def test_contains_inappropriate_content_true(self):
        """不適切なコンテンツ含有一致テスト"""
        text = "不適切なアプリ"
        result = self.subtitle_generator._contains_inappropriate_content(text)
        assert result is True

    def test_contains_inappropriate_content_false(self):
        """不適切なコンテンツ非含有テスト"""
        text = "便利なアプリ"
        result = self.subtitle_generator._contains_inappropriate_content(text)
        assert result is False

    def test_post_process_subtitle(self):
        """サブタイトル後処理テスト"""
        subtitle = "  テストアプリ。  "
        result = self.subtitle_generator._post_process_subtitle(subtitle, "テスト")
        assert "テスト" not in result
        assert len(result) <= 30

    @patch('app.services.subtitle_generator.PromptManager')
    def test_prepare_strict_prompt(self, mock_prompt_manager):
        """厳格なプロンプト準備テスト"""
        mock_prompt_manager.get_subtitle_prompt.return_value = "基本プロンプト"
        
        prompt = self.subtitle_generator._prepare_strict_prompt(
            self.test_app_info, "テスト", "ja"
        )
        
        assert "基本プロンプト" in prompt
        assert "30文字以内" in prompt
        assert "主要キーワード「テスト」" in prompt

    def test_generate_fallback_subtitle_ja(self):
        """日本語フォールバックサブタイトル生成テスト"""
        app_info = {"features": "便利な機能、使いやすいインターフェース"}
        result = self.subtitle_generator._generate_fallback_subtitle(app_info, "ja")
        assert len(result) <= 30
        assert "便利な機能" in result

    def test_generate_fallback_subtitle_en(self):
        """英語フォールバックサブタイトル生成テスト"""
        app_info = {"features": "Useful features, Easy interface"}
        result = self.subtitle_generator._generate_fallback_subtitle(app_info, "en")
        assert len(result) <= 30
        assert "Useful features" in result

    def test_generate_fallback_subtitle_no_features(self):
        """特徴なしのフォールバックサブタイトル生成テスト"""
        app_info = {}
        result_ja = self.subtitle_generator._generate_fallback_subtitle(app_info, "ja")
        result_en = self.subtitle_generator._generate_fallback_subtitle(app_info, "en")
        
        assert result_ja == "便利なアプリ"
        assert result_en == "Useful App"

    @patch.object(SubtitleGenerator, '_prepare_prompt')
    @patch.object(SubtitleGenerator, '_post_process_subtitle')
    @patch.object(SubtitleGenerator, '_validate_subtitle')
    def test_generate_subtitle_success(self, mock_validate, mock_post_process, mock_prepare):
        """サブタイトル生成成功テスト"""
        mock_prepare.return_value = "テストプロンプト"
        self.mock_gemini.generate_subtitle.return_value = "便利なアプリ"
        mock_post_process.return_value = "便利なアプリ"
        mock_validate.return_value = True
        
        result = self.subtitle_generator.generate_subtitle(
            self.test_app_info, "テスト", "ja"
        )
        
        assert result == "便利なアプリ"
        self.mock_gemini.generate_subtitle.assert_called_once_with("テストプロンプト", "ja")

    @patch.object(SubtitleGenerator, '_prepare_prompt')
    @patch.object(SubtitleGenerator, '_post_process_subtitle')
    @patch.object(SubtitleGenerator, '_validate_subtitle')
    @patch.object(SubtitleGenerator, '_regenerate_subtitle')
    def test_generate_subtitle_validation_failure(self, mock_regenerate, mock_validate, mock_post_process, mock_prepare):
        """サブタイトル生成検証失敗テスト"""
        mock_prepare.return_value = "テストプロンプト"
        self.mock_gemini.generate_subtitle.return_value = "テストアプリ"
        mock_post_process.return_value = "テストアプリ"
        mock_validate.return_value = False
        mock_regenerate.return_value = "便利なアプリ"
        
        result = self.subtitle_generator.generate_subtitle(
            self.test_app_info, "テスト", "ja"
        )
        
        assert result == "便利なアプリ"
        mock_regenerate.assert_called_once_with(self.test_app_info, "テスト", "ja")

    @patch.object(SubtitleGenerator, '_prepare_prompt')
    def test_generate_subtitle_api_error(self, mock_prepare):
        """サブタイトル生成APIエラーテスト"""
        mock_prepare.return_value = "テストプロンプト"
        self.mock_gemini.generate_subtitle.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            self.subtitle_generator.generate_subtitle(
                self.test_app_info, "テスト", "ja"
            )

    @patch.object(SubtitleGenerator, '_prepare_strict_prompt')
    @patch.object(SubtitleGenerator, '_post_process_subtitle')
    @patch.object(SubtitleGenerator, '_validate_subtitle')
    @patch.object(SubtitleGenerator, '_generate_fallback_subtitle')
    def test_regenerate_subtitle_success(self, mock_fallback, mock_validate, mock_post_process, mock_prepare):
        """サブタイトル再生成成功テスト"""
        mock_prepare.return_value = "厳格プロンプト"
        self.mock_gemini.generate_subtitle.return_value = "便利なアプリ"
        mock_post_process.return_value = "便利なアプリ"
        mock_validate.return_value = True
        
        result = self.subtitle_generator._regenerate_subtitle(
            self.test_app_info, "テスト", "ja"
        )
        
        assert result == "便利なアプリ"
        self.mock_gemini.generate_subtitle.assert_called_once_with("厳格プロンプト", "ja")

    @patch.object(SubtitleGenerator, '_prepare_strict_prompt')
    @patch.object(SubtitleGenerator, '_post_process_subtitle')
    @patch.object(SubtitleGenerator, '_validate_subtitle')
    @patch.object(SubtitleGenerator, '_generate_fallback_subtitle')
    def test_regenerate_subtitle_fallback(self, mock_fallback, mock_validate, mock_post_process, mock_prepare):
        """サブタイトル再生成フォールバックテスト"""
        mock_prepare.return_value = "厳格プロンプト"
        self.mock_gemini.generate_subtitle.return_value = "テストアプリ"
        mock_post_process.return_value = "テストアプリ"
        mock_validate.return_value = False
        mock_fallback.return_value = "便利なアプリ"
        
        result = self.subtitle_generator._regenerate_subtitle(
            self.test_app_info, "テスト", "ja"
        )
        
        assert result == "便利なアプリ"
        mock_fallback.assert_called_once_with(self.test_app_info, "ja")

    @patch.object(SubtitleGenerator, '_prepare_strict_prompt')
    @patch.object(SubtitleGenerator, '_generate_fallback_subtitle')
    def test_regenerate_subtitle_api_error(self, mock_fallback, mock_prepare):
        """サブタイトル再生成APIエラーテスト"""
        mock_prepare.return_value = "厳格プロンプト"
        self.mock_gemini.generate_subtitle.side_effect = Exception("API Error")
        mock_fallback.return_value = "便利なアプリ"
        
        result = self.subtitle_generator._regenerate_subtitle(
            self.test_app_info, "テスト", "ja"
        )
        
        assert result == "便利なアプリ"
        mock_fallback.assert_called_once_with(self.test_app_info, "ja")


class TestSubtitleGeneratorIntegration:
    """SubtitleGenerator統合テスト"""

    def test_character_limit_enforcement(self):
        """文字数制限の強制テスト"""
        generator = SubtitleGenerator(Mock())
        
        # 30文字を超えるサブタイトル
        long_subtitle = "これは30文字を超える非常に長いサブタイトルです"
        adjusted = generator._adjust_length(long_subtitle, 30)
        
        assert len(adjusted) <= 30

    def test_keyword_exclusion(self):
        """キーワード除外テスト"""
        generator = SubtitleGenerator(Mock())
        
        # キーワードを含むサブタイトル
        subtitle_with_keyword = "テストアプリは便利です"
        filtered = generator._filter_keywords(subtitle_with_keyword, ["テスト"])
        
        assert "テスト" not in filtered

    def test_validation_comprehensive(self):
        """包括的な検証テスト"""
        generator = SubtitleGenerator(Mock())
        
        # 有効なサブタイトル
        valid_subtitle = "便利なアプリ"
        assert generator._validate_subtitle(valid_subtitle, "テスト") is True
        
        # 無効なサブタイトル（キーワードを含む）
        invalid_subtitle = "テストアプリ"
        assert generator._validate_subtitle(invalid_subtitle, "テスト") is False
