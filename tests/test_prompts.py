"""
プロンプト管理システムのテスト
"""

import pytest
from app.services.prompts import PromptManager, JapanesePrompts, EnglishPrompts


class TestPromptManager:
    """PromptManagerクラスのテスト"""
    
    def test_get_supported_languages(self):
        """サポートされている言語の取得テスト"""
        languages = PromptManager.get_supported_languages()
        assert "ja" in languages
        assert "en" in languages
        assert len(languages) == 2
    
    def test_get_available_prompt_types(self):
        """利用可能なプロンプトタイプの取得テスト"""
        prompt_types = PromptManager.get_available_prompt_types()
        expected_types = ["TITLE_GENERATION", "SUBTITLE_GENERATION", "DESCRIPTION_GENERATION", "KEYWORDS_GENERATION"]
        
        for expected_type in expected_types:
            assert expected_type in prompt_types
    
    def test_get_prompt_unsupported_language(self):
        """サポートされていない言語でのエラーテスト"""
        with pytest.raises(ValueError, match="Unsupported language"):
            PromptManager.get_prompt("fr", "TITLE_GENERATION")
    
    def test_get_prompt_unsupported_type(self):
        """サポートされていないプロンプトタイプでのエラーテスト"""
        with pytest.raises(ValueError, match="Unsupported prompt type"):
            PromptManager.get_prompt("ja", "INVALID_TYPE")
    
    def test_get_subtitle_prompt_ja(self):
        """日本語サブタイトル生成プロンプトのテスト"""
        prompt = PromptManager.get_subtitle_prompt(
            language="ja",
            app_name="テストアプリ",
            app_features="便利な機能",
            main_keyword="テスト",
            target_audience="一般ユーザー"
        )
        
        assert "テストアプリ" in prompt
        assert "便利な機能" in prompt
        assert "テスト" in prompt
        assert "一般ユーザー" in prompt
        assert "30文字以内" in prompt
        assert "主要キーワード" in prompt
        assert "含めない" in prompt
    
    def test_get_subtitle_prompt_en(self):
        """英語サブタイトル生成プロンプトのテスト"""
        prompt = PromptManager.get_subtitle_prompt(
            language="en",
            app_name="Test App",
            app_features="Useful features",
            main_keyword="test",
            target_audience="General users"
        )
        
        assert "Test App" in prompt
        assert "Useful features" in prompt
        assert "test" in prompt
        assert "General users" in prompt
        assert "30 characters" in prompt
        assert "Exclude main keyword" in prompt
    
    def test_get_description_prompt_ja(self):
        """日本語概要生成プロンプトのテスト"""
        prompt = PromptManager.get_description_prompt(
            language="ja",
            app_name="テストアプリ",
            app_features="便利な機能",
            main_keyword="テスト",
            related_keywords="関連キーワード1,関連キーワード2",
            target_audience="一般ユーザー"
        )
        
        assert "テストアプリ" in prompt
        assert "便利な機能" in prompt
        assert "テスト" in prompt
        assert "関連キーワード1,関連キーワード2" in prompt
        assert "一般ユーザー" in prompt
        assert "4000文字以内" in prompt
        assert "4〜7回程度自然に含める" in prompt
    
    def test_get_description_prompt_en(self):
        """英語概要生成プロンプトのテスト"""
        prompt = PromptManager.get_description_prompt(
            language="en",
            app_name="Test App",
            app_features="Useful features",
            main_keyword="test",
            related_keywords="related1,related2",
            target_audience="General users"
        )
        
        assert "Test App" in prompt
        assert "Useful features" in prompt
        assert "test" in prompt
        assert "related1,related2" in prompt
        assert "General users" in prompt
        assert "4000 characters" in prompt
        assert "4-7 times" in prompt
    
    def test_get_title_prompt_ja(self):
        """日本語タイトル生成プロンプトのテスト"""
        prompt = PromptManager.get_title_prompt(
            language="ja",
            app_info="テストアプリの情報",
            keywords="テスト,キーワード"
        )
        
        assert "テストアプリの情報" in prompt
        assert "テスト,キーワード" in prompt
        assert "30文字以内" in prompt
    
    def test_get_title_prompt_en(self):
        """英語タイトル生成プロンプトのテスト"""
        prompt = PromptManager.get_title_prompt(
            language="en",
            app_info="Test app info",
            keywords="test,keyword"
        )
        
        assert "Test app info" in prompt
        assert "test,keyword" in prompt
        assert "30 characters" in prompt
    
    def test_get_keywords_prompt_ja(self):
        """日本語キーワード文字列生成プロンプトのテスト"""
        prompt = PromptManager.get_keywords_prompt(
            language="ja",
            keywords="テスト,キーワード"
        )
        
        assert "テスト,キーワード" in prompt
        assert "100文字以内" in prompt
        assert "カンマ区切り" in prompt
    
    def test_get_keywords_prompt_en(self):
        """英語キーワード文字列生成プロンプトのテスト"""
        prompt = PromptManager.get_keywords_prompt(
            language="en",
            keywords="test,keyword"
        )
        
        assert "test,keyword" in prompt
        assert "100 characters" in prompt
        assert "Comma separated" in prompt


class TestJapanesePrompts:
    """JapanesePromptsクラスのテスト"""
    
    def test_subtitle_generation_prompt(self):
        """サブタイトル生成プロンプトの内容テスト"""
        prompt = JapanesePrompts.SUBTITLE_GENERATION
        
        # 必須要素の確認
        assert "30文字以内" in prompt
        assert "主要キーワード" in prompt
        assert "含めない" in prompt
        assert "アプリの価値" in prompt
        assert "魅力的" in prompt
    
    def test_description_generation_prompt(self):
        """概要生成プロンプトの内容テスト"""
        prompt = JapanesePrompts.DESCRIPTION_GENERATION
        
        # 必須要素の確認
        assert "4000文字以内" in prompt
        assert "4〜7回程度自然に含める" in prompt
        assert "アプリの価値提案" in prompt
        assert "ユーザーの問題解決" in prompt
        assert "主要機能" in prompt
    
    def test_title_generation_prompt(self):
        """タイトル生成プロンプトの内容テスト"""
        prompt = JapanesePrompts.TITLE_GENERATION
        
        # 必須要素の確認
        assert "30文字以内" in prompt
        assert "主要キーワード" in prompt
        assert "魅力的" in prompt
        assert "覚えやすい" in prompt
    
    def test_keywords_generation_prompt(self):
        """キーワード文字列生成プロンプトの内容テスト"""
        prompt = JapanesePrompts.KEYWORDS_GENERATION
        
        # 必須要素の確認
        assert "100文字以内" in prompt
        assert "カンマ区切り" in prompt
        assert "関連性の高い順" in prompt


class TestEnglishPrompts:
    """EnglishPromptsクラスのテスト"""
    
    def test_subtitle_generation_prompt(self):
        """サブタイトル生成プロンプトの内容テスト"""
        prompt = EnglishPrompts.SUBTITLE_GENERATION
        
        # 必須要素の確認
        assert "30 characters" in prompt
        assert "Exclude main keyword" in prompt
        assert "Express app value" in prompt
        assert "Memorable" in prompt
    
    def test_description_generation_prompt(self):
        """概要生成プロンプトの内容テスト"""
        prompt = EnglishPrompts.DESCRIPTION_GENERATION
        
        # 必須要素の確認
        assert "4000 characters" in prompt
        assert "4-7 times" in prompt
        assert "value proposition" in prompt
        assert "problem solving" in prompt
        assert "main features" in prompt
    
    def test_title_generation_prompt(self):
        """タイトル生成プロンプトの内容テスト"""
        prompt = EnglishPrompts.TITLE_GENERATION
        
        # 必須要素の確認
        assert "30 characters" in prompt
        assert "Include main keywords" in prompt
        assert "Attractive" in prompt
        assert "memorable" in prompt
    
    def test_keywords_generation_prompt(self):
        """キーワード文字列生成プロンプトの内容テスト"""
        prompt = EnglishPrompts.KEYWORDS_GENERATION
        
        # 必須要素の確認
        assert "100 characters" in prompt
        assert "Comma separated" in prompt
        assert "Ordered by relevance" in prompt


class TestPromptConstraints:
    """プロンプト制約のテスト"""
    
    def test_subtitle_character_limit_ja(self):
        """日本語サブタイトル生成プロンプトの文字数制限確認"""
        prompt = JapanesePrompts.SUBTITLE_GENERATION
        assert "30文字以内（厳守）" in prompt
    
    def test_subtitle_character_limit_en(self):
        """英語サブタイトル生成プロンプトの文字数制限確認"""
        prompt = EnglishPrompts.SUBTITLE_GENERATION
        assert "30 characters (strictly enforced)" in prompt
    
    def test_description_character_limit_ja(self):
        """日本語概要生成プロンプトの文字数制限確認"""
        prompt = JapanesePrompts.DESCRIPTION_GENERATION
        assert "4000文字以内（厳守）" in prompt
    
    def test_description_character_limit_en(self):
        """英語概要生成プロンプトの文字数制限確認"""
        prompt = EnglishPrompts.DESCRIPTION_GENERATION
        assert "4000 characters (strictly enforced)" in prompt
    
    def test_keyword_constraint_ja(self):
        """日本語プロンプトのキーワード制約確認"""
        subtitle_prompt = JapanesePrompts.SUBTITLE_GENERATION
        description_prompt = JapanesePrompts.DESCRIPTION_GENERATION
        
        assert "主要キーワード" in subtitle_prompt and "含めない" in subtitle_prompt
        assert "主要キーワード" in description_prompt and "4〜7回程度自然に含める" in description_prompt
    
    def test_keyword_constraint_en(self):
        """英語プロンプトのキーワード制約確認"""
        subtitle_prompt = EnglishPrompts.SUBTITLE_GENERATION
        description_prompt = EnglishPrompts.DESCRIPTION_GENERATION
        
        assert "Exclude main keyword" in subtitle_prompt
        assert "include main keyword" in description_prompt and "4-7 times" in description_prompt
