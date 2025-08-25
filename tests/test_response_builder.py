"""
レスポンスビルダーのテスト
"""

from datetime import datetime

import pytest

from app.models.response_models import (
    ASOTextGenerationResponse,
    DescriptionResponse,
    KeywordFieldResponse,
    SubtitleResponse,
    TitleResponse,
    WhatsNewResponse,
)
from app.utils.response_builder import ResponseBuilder


class TestResponseBuilder:
    """レスポンスビルダーのテストクラス"""

    def setup_method(self):
        """各テストメソッドの前処理"""
        self.response_builder = ResponseBuilder()

    def test_build_integrated_response(self):
        """統合レスポンスの構築テスト"""
        # テストデータ
        keyword_field = "フィットネス トレーニング 健康管理"
        title = "FitTracker - 健康管理アプリ"
        subtitle = "あなたの健康をサポート"
        description = "FitTrackerは、あなたの健康管理をサポートする総合的なフィットネスアプリです。"
        whats_new = "新機能として、より詳細な運動分析機能を追加しました。"
        language = "ja"

        # レスポンス構築
        response = self.response_builder.build_integrated_response(
            keyword_field=keyword_field,
            title=title,
            subtitle=subtitle,
            description=description,
            whats_new=whats_new,
            language=language,
        )

        # 検証
        assert isinstance(response, ASOTextGenerationResponse)
        assert response.keyword_field == keyword_field
        assert response.title == title
        assert response.subtitle == subtitle
        assert response.description == description
        assert response.whats_new == whats_new
        assert response.language == language
        assert response.processing_time is not None
        assert response.generated_at is not None

    def test_build_keyword_field_response(self):
        """キーワードフィールドレスポンスの構築テスト"""
        keyword_field = "フィットネス トレーニング 健康管理"
        language = "ja"

        response = self.response_builder.build_keyword_field_response(
            keyword_field=keyword_field, language=language
        )

        assert isinstance(response, KeywordFieldResponse)
        assert response.keyword_field == keyword_field
        assert response.language == language
        assert response.processing_time is not None
        assert response.generated_at is not None

    def test_build_title_response(self):
        """タイトルレスポンスの構築テスト"""
        title = "FitTracker - 健康管理アプリ"
        language = "ja"

        response = self.response_builder.build_title_response(
            title=title, language=language
        )

        assert isinstance(response, TitleResponse)
        assert response.title == title
        assert response.language == language
        assert response.processing_time is not None
        assert response.generated_at is not None

    def test_build_subtitle_response(self):
        """サブタイトルレスポンスの構築テスト"""
        subtitle = "あなたの健康をサポート"
        language = "ja"

        response = self.response_builder.build_subtitle_response(
            subtitle=subtitle, language=language
        )

        assert isinstance(response, SubtitleResponse)
        assert response.subtitle == subtitle
        assert response.language == language
        assert response.processing_time is not None
        assert response.generated_at is not None

    def test_build_description_response(self):
        """概要レスポンスの構築テスト"""
        description = "FitTrackerは、あなたの健康管理をサポートする総合的なフィットネスアプリです。"
        language = "ja"

        response = self.response_builder.build_description_response(
            description=description, language=language
        )

        assert isinstance(response, DescriptionResponse)
        assert response.description == description
        assert response.language == language
        assert response.processing_time is not None
        assert response.generated_at is not None

    def test_build_whats_new_response(self):
        """最新情報レスポンスの構築テスト"""
        whats_new = "新機能として、より詳細な運動分析機能を追加しました。"
        language = "ja"

        response = self.response_builder.build_whats_new_response(
            whats_new=whats_new, language=language
        )

        assert isinstance(response, WhatsNewResponse)
        assert response.whats_new == whats_new
        assert response.language == language
        assert response.processing_time is not None
        assert response.generated_at is not None

    def test_processing_time_accuracy(self):
        """処理時間の正確性テスト"""
        import time

        # 少し時間のかかる処理をシミュレート
        response_builder = ResponseBuilder()
        time.sleep(0.1)  # 100ms待機

        response = response_builder.build_title_response(
            title="Test Title", language="ja"
        )

        # 処理時間が0.1秒以上であることを確認
        assert response.processing_time >= 0.1
        assert response.processing_time < 1.0  # 1秒未満であることを確認

    def test_character_limit_validation(self):
        """文字数制限のバリデーションテスト"""
        # 30文字制限のテスト（タイトル）
        long_title = "A" * 31  # 31文字

        with pytest.raises(ValueError):
            self.response_builder.build_title_response(title=long_title, language="ja")

        # 100文字制限のテスト（キーワードフィールド）
        long_keyword_field = "A" * 101  # 101文字

        with pytest.raises(ValueError):
            self.response_builder.build_keyword_field_response(
                keyword_field=long_keyword_field, language="ja"
            )

    def test_language_validation(self):
        """言語バリデーションテスト"""
        # 日本語
        response_ja = self.response_builder.build_title_response(
            title="テストタイトル", language="ja"
        )
        assert response_ja.language == "ja"

        # 英語
        response_en = self.response_builder.build_title_response(
            title="Test Title", language="en"
        )
        assert response_en.language == "en"
