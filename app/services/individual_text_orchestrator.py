from typing import Dict, Any
from fastapi import UploadFile
from app.services.csv_analyzer import CSVAnalyzer
from app.services.keyword_selector import KeywordSelector
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.title_generator import TitleGenerator
from app.services.subtitle_generator import SubtitleGenerator
from app.services.description_generator import DescriptionGenerator
from app.services.whats_new_generator import WhatsNewGenerator

class IndividualTextOrchestrator:
    """
    個別テキスト生成の効率的な処理フローを管理するオーケストレーター
    """

    def __init__(self):
        self.csv_analyzer = CSVAnalyzer()
        self.keyword_selector = KeywordSelector()
        self.keyword_field_generator = KeywordFieldGenerator()
        self.title_generator = TitleGenerator()
        self.subtitle_generator = SubtitleGenerator()
        self.description_generator = DescriptionGenerator()
        self.whats_new_generator = WhatsNewGenerator()

    async def generate_keyword_field(self, csv_file: UploadFile, language: str) -> str:
        """
        キーワードフィールド生成の効率的な処理フロー

        Args:
            csv_file: キーワードCSVファイル
            language: 生成言語

        Returns:
            str: 生成されたキーワードフィールド
        """
        # CSV分析とキーワード選定
        keywords_data = await self.csv_analyzer.analyze_csv(csv_file)
        primary_keyword = self.keyword_selector.select_primary_keyword(keywords_data)

        # キーワードフィールド生成
        return await self.keyword_field_generator.generate(
            keywords_data, primary_keyword, language
        )

    async def generate_title(self, primary_keyword: str, app_name: str, language: str) -> str:
        """
        タイトル生成の効率的な処理フロー

        Args:
            primary_keyword: 主要キーワード
            app_name: アプリ名
            language: 生成言語

        Returns:
            str: 生成されたタイトル
        """
        return await self.title_generator.generate(
            primary_keyword, app_name, language
        )

    async def generate_subtitle(self, primary_keyword: str, features: list, language: str) -> str:
        """
        サブタイトル生成の効率的な処理フロー

        Args:
            primary_keyword: 主要キーワード
            features: アプリの特徴リスト
            language: 生成言語

        Returns:
            str: 生成されたサブタイトル
        """
        return await self.subtitle_generator.generate(
            primary_keyword, features, language
        )

    async def generate_description(self, primary_keyword: str, features: list, language: str) -> str:
        """
        概要生成の効率的な処理フロー

        Args:
            primary_keyword: 主要キーワード
            features: アプリの特徴リスト
            language: 生成言語

        Returns:
            str: 生成された概要
        """
        return await self.description_generator.generate(
            primary_keyword, features, language
        )

    async def generate_whats_new(self, features: list, language: str) -> str:
        """
        最新情報生成の効率的な処理フロー

        Args:
            features: アプリの特徴リスト
            language: 生成言語

        Returns:
            str: 生成された最新情報
        """
        return await self.whats_new_generator.generate(
            features, language
        )
