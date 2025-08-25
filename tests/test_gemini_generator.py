"""
GeminiGeneratorクラスのテスト
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.gemini_generator import GeminiGenerator


class TestGeminiGenerator:
    """GeminiGeneratorクラスのテスト"""

    @pytest.fixture
    def mock_genai(self):
        """google.genaiのモック"""
        with patch("app.services.gemini_generator.genai") as mock_genai:
            mock_client = Mock()
            mock_genai.Client.return_value = mock_client
            yield mock_genai

    @pytest.fixture
    def mock_settings(self):
        """設定のモック"""
        with patch("app.services.gemini_generator.settings") as mock_settings:
            mock_settings.gemini_api_key = None
            mock_settings.google_api_key = "test_api_key"
            mock_settings.gemini_model = "gemini-2.5-flash"
            mock_settings.RECOMMENDED_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]
            mock_settings.ACCEPTABLE_MODELS = ["gemini-2.0-flash", "gemini-2.0-pro"]
            mock_settings.DEPRECATED_MODELS = [
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-pro",
            ]
            mock_settings.available_models = [
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-2.0-flash",
                "gemini-2.0-pro",
            ]
            mock_settings.is_valid_model = lambda x: x in mock_settings.available_models
            mock_settings.get_model_category = lambda x: (
                "recommended"
                if x in mock_settings.RECOMMENDED_MODELS
                else (
                    "acceptable"
                    if x in mock_settings.ACCEPTABLE_MODELS
                    else (
                        "deprecated"
                        if x in mock_settings.DEPRECATED_MODELS
                        else "unknown"
                    )
                )
            )
            mock_settings.gemini_timeout = 30
            mock_settings.gemini_max_retries = 3
            yield mock_settings

    @pytest.fixture
    def gemini_generator(self, mock_genai, mock_settings):
        """GeminiGeneratorインスタンス"""
        return GeminiGenerator()

    def test_init_with_api_key(self, mock_genai, mock_settings):
        """APIキーを指定して初期化するテスト"""
        generator = GeminiGenerator(api_key="custom_api_key")
        assert generator.api_key == "custom_api_key"
        mock_genai.Client.assert_called_once_with(api_key="custom_api_key")

    def test_init_without_api_key(self, mock_genai, mock_settings):
        """APIキーなしで初期化するテスト"""
        generator = GeminiGenerator()
        assert generator.api_key == "test_api_key"
        assert generator.model_name == "gemini-2.5-flash"
        mock_genai.Client.assert_called_once_with(api_key="test_api_key")

    def test_init_with_custom_model(self, mock_genai, mock_settings):
        """カスタムモデルでの初期化テスト"""
        generator = GeminiGenerator(model_name="gemini-2.5-pro")
        assert generator.model_name == "gemini-2.5-pro"

    def test_init_with_deprecated_model(self, mock_genai, mock_settings):
        """非推奨モデルでの初期化テスト（エラー）"""
        with pytest.raises(ValueError, match="非推奨モデル"):
            GeminiGenerator(model_name="gemini-pro")

    def test_init_with_invalid_model(self, mock_genai, mock_settings):
        """無効なモデルでの初期化テスト（エラー）"""
        with pytest.raises(ValueError, match="無効なモデル"):
            GeminiGenerator(model_name="invalid-model")

    def test_init_no_api_key_available(self, mock_genai, mock_settings):
        """APIキーが利用できない場合のテスト"""
        mock_settings.google_api_key = None
        with pytest.raises(ValueError, match="Gemini API key is required"):
            GeminiGenerator()

    def test_generate_subtitle_success(self, gemini_generator, mock_genai):
        """サブタイトル生成成功のテスト"""
        mock_response = Mock()
        mock_response.text = "テストサブタイトル"
        gemini_generator.client.models.generate_content.return_value = mock_response

        result = gemini_generator.generate_subtitle("テストプロンプト")

        assert result == "テストサブタイトル"
        gemini_generator.client.models.generate_content.assert_called_once()

    def test_generate_subtitle_length_limit(self, gemini_generator, mock_genai):
        """サブタイトル文字数制限のテスト"""
        long_text = "これは非常に長いサブタイトルで、30文字を超えています。"
        mock_response = Mock()
        mock_response.text = long_text
        gemini_generator.client.models.generate_content.return_value = mock_response

        result = gemini_generator.generate_subtitle("テストプロンプト")

        assert len(result) <= 30
        assert result.endswith("。")

    def test_generate_description_success(self, gemini_generator, mock_genai):
        """概要生成成功のテスト"""
        mock_response = Mock()
        mock_response.text = "これはテスト用の概要です。"
        gemini_generator.client.models.generate_content.return_value = mock_response

        result = gemini_generator.generate_description("テストプロンプト")

        assert result == "これはテスト用の概要です。"
        gemini_generator.client.models.generate_content.assert_called_once()

    def test_generate_description_length_limit(self, gemini_generator, mock_genai):
        """概要文字数制限のテスト"""
        long_text = "長いテキスト" * 1000  # 4000文字を超えるテキスト
        mock_response = Mock()
        mock_response.text = long_text
        gemini_generator.client.models.generate_content.return_value = mock_response

        result = gemini_generator.generate_description("テストプロンプト")

        assert len(result) <= 4000

    def test_call_gemini_api_success(self, gemini_generator, mock_genai):
        """API呼び出し成功のテスト"""
        mock_response = Mock()
        mock_response.text = "API応答"
        gemini_generator.client.models.generate_content.return_value = mock_response

        result = gemini_generator._call_gemini_api("テストプロンプト")

        assert result == "API応答"
        gemini_generator.client.models.generate_content.assert_called_once()

    def test_call_gemini_api_with_retry(self, gemini_generator, mock_genai):
        """API呼び出しリトライのテスト"""
        mock_response = Mock()
        mock_response.text = "API応答"

        # 最初の2回は失敗、3回目で成功
        gemini_generator.client.models.generate_content.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            mock_response,
        ]

        result = gemini_generator._call_gemini_api("テストプロンプト")

        assert result == "API応答"
        assert gemini_generator.client.models.generate_content.call_count == 3

    def test_call_gemini_api_max_retries_exceeded(self, gemini_generator, mock_genai):
        """最大リトライ回数超過のテスト"""
        gemini_generator.client.models.generate_content.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(Exception, match="API Error"):
            gemini_generator._call_gemini_api("テストプロンプト")

        assert gemini_generator.client.models.generate_content.call_count == 3

    def test_validate_text_length_within_limit(self, gemini_generator):
        """文字数制限内のテキスト検証テスト"""
        text = "短いテキスト"
        result = gemini_generator._validate_text_length(text, 20)
        assert result == text

    def test_validate_text_length_exceeds_limit(self, gemini_generator):
        """文字数制限超過のテキスト検証テスト"""
        text = "これは非常に長いテキストで、制限を超えています。"
        result = gemini_generator._validate_text_length(text, 10)
        assert len(result) <= 10

    def test_validate_text_length_with_period(self, gemini_generator):
        """句読点を考慮した文字数調整テスト"""
        text = "これは最初の文です。これは二番目の文です。"
        result = gemini_generator._validate_text_length(text, 15)
        assert result.endswith("。")

    def test_analyze_keywords_success(self, gemini_generator, mock_genai):
        """キーワード分析成功のテスト"""
        mock_response = Mock()
        mock_response.text = "キーワード1, キーワード2, キーワード3"
        gemini_generator.client.models.generate_content.return_value = mock_response

        result = gemini_generator.analyze_keywords("テストテキスト")

        expected = ["キーワード1", "キーワード2", "キーワード3"]
        assert result == expected

    def test_analyze_keywords_failure(self, gemini_generator, mock_genai):
        """キーワード分析失敗のテスト"""
        gemini_generator.client.models.generate_content.side_effect = Exception(
            "API Error"
        )

        result = gemini_generator.analyze_keywords("テストテキスト")

        assert result == []

    def test_optimize_text_success(self, gemini_generator, mock_genai):
        """テキスト最適化成功のテスト"""
        mock_response = Mock()
        mock_response.text = "最適化されたテキスト"
        gemini_generator.client.models.generate_content.return_value = mock_response

        result = gemini_generator.optimize_text("元のテキスト", 50)

        assert result == "最適化されたテキスト"

    def test_optimize_text_failure(self, gemini_generator, mock_genai):
        """テキスト最適化失敗のテスト"""
        gemini_generator.client.models.generate_content.side_effect = Exception(
            "API Error"
        )

        original_text = "元のテキスト"
        result = gemini_generator.optimize_text(original_text, 50)

        assert result == original_text
