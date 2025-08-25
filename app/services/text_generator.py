"""
テキスト生成サービス
ASOテキストの生成を行うサービス
"""

from typing import Any, Dict, List

from app.services.gemini_generator import GeminiGenerator
from app.services.keyword_field_generator import KeywordFieldGenerationService
from app.services.subtitle_generator import SubtitleGenerator
from app.services.title_generator import TitleGenerationService
from app.services.whats_new_generator import WhatsNewGenerationService


class TextGenerator:
    """テキスト生成クラス"""

    def __init__(self):
        """初期化"""
        self.gemini_generator = GeminiGenerator()
        self.keyword_field_service = KeywordFieldGenerationService()
        self.title_service = TitleGenerationService()
        self.whats_new_service = WhatsNewGenerationService()
        self.subtitle_generator = SubtitleGenerator(self.gemini_generator)

    def generate_title(self, keywords: List[str], app_info: Dict[str, Any]) -> str:
        """
        アプリタイトルを生成する

        Args:
            keywords: キーワードのリスト
            app_info: アプリ情報の辞書

        Returns:
            生成されたタイトル
        """
        pass

    def generate_title_from_keyword(
        self,
        primary_keyword: str,
        app_base_name: str,
        language: str = "ja"
    ) -> Dict[str, Any]:
        """
        主要キーワードとアプリ基本名からタイトルを生成する

        Args:
            primary_keyword: 主要キーワード
            app_base_name: アプリ基本名
            language: 言語

        Returns:
            生成されたタイトル
        """
        return self.title_service.generate_title(primary_keyword, app_base_name, language)

    def generate_subtitle(
        self,
        app_info: Dict[str, Any],
        main_keyword: str,
        language: str = "ja"
    ) -> str:
        """
        サブタイトルを生成する

        Args:
            app_info: アプリ情報（名前、特徴、ターゲットユーザーなど）
            main_keyword: 主要キーワード（除外対象）
            language: 生成言語（"ja" or "en"）

        Returns:
            生成されたサブタイトル（30文字以内）
        """
        return self.subtitle_generator.generate_subtitle(app_info, main_keyword, language)

    def generate_description(
        self, keywords: List[str], app_info: Dict[str, Any]
    ) -> str:
        """
        アプリ説明文を生成する

        Args:
            keywords: キーワードのリスト
            app_info: アプリ情報の辞書

        Returns:
            生成された説明文
        """
        pass

    def generate_whats_new(
        self,
        primary_keyword: str,
        app_features: List[str],
        language: str = "ja"
    ) -> Dict[str, Any]:
        """
        最新情報を生成する

        Args:
            primary_keyword: 主要キーワード
            app_features: アプリの特徴リスト
            language: 言語

        Returns:
            生成された最新情報
        """
        return self.whats_new_service.generate_whats_new(primary_keyword, app_features, language)

    def generate_keywords(self, keywords: List[str], app_info: Dict[str, Any]) -> str:
        """
        キーワード文字列を生成する

        Args:
            keywords: キーワードのリスト
            app_info: アプリ情報の辞書

        Returns:
            生成されたキーワード文字列
        """
        pass

    def generate_keyword_field(
        self,
        selection_result: Dict[str, Any],
        language: str = "ja"
    ) -> Dict[str, Any]:
        """
        キーワードフィールドを生成する

        Args:
            selection_result: キーワード選定結果
            language: 言語

        Returns:
            生成されたキーワードフィールド
        """
        return self.keyword_field_service.generate_keyword_field(selection_result, language)
