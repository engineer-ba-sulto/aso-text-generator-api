"""
多言語プロンプト管理モジュール
"""

from typing import Dict, Any, Optional
from .en import EnglishPrompts
from .ja import JapanesePrompts

__all__ = ["JapanesePrompts", "EnglishPrompts", "PromptManager"]


class PromptManager:
    """プロンプト管理クラス"""
    
    SUPPORTED_LANGUAGES = {
        "ja": JapanesePrompts,
        "en": EnglishPrompts
    }
    
    @classmethod
    def get_prompt(cls, language: str, prompt_type: str, **kwargs) -> str:
        """
        指定された言語とタイプのプロンプトを取得し、パラメータを置換する
        
        Args:
            language: 言語コード ("ja" または "en")
            prompt_type: プロンプトタイプ ("TITLE_GENERATION", "SUBTITLE_GENERATION", "DESCRIPTION_GENERATION", "KEYWORDS_GENERATION")
            **kwargs: プロンプトパラメータ
            
        Returns:
            パラメータが置換されたプロンプト文字列
            
        Raises:
            ValueError: サポートされていない言語またはプロンプトタイプの場合
        """
        if language not in cls.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}. Supported: {list(cls.SUPPORTED_LANGUAGES.keys())}")
        
        prompt_class = cls.SUPPORTED_LANGUAGES[language]
        
        if not hasattr(prompt_class, prompt_type):
            raise ValueError(f"Unsupported prompt type: {prompt_type}. Available: {[attr for attr in dir(prompt_class) if not attr.startswith('_')]}")
        
        prompt_template = getattr(prompt_class, prompt_type)
        
        # パラメータのデフォルト値を設定
        default_params = {
            "app_name": "",
            "app_features": "",
            "main_keyword": "",
            "related_keywords": "",
            "target_audience": "",
            "app_info": "",
            "keywords": ""
        }
        
        # 提供されたパラメータでデフォルト値を上書き
        params = {**default_params, **kwargs}
        
        return prompt_template.format(**params)
    
    @classmethod
    def get_subtitle_prompt(cls, language: str, app_name: str, app_features: str, 
                           main_keyword: str, target_audience: str) -> str:
        """
        サブタイトル生成プロンプトを取得
        
        Args:
            language: 言語コード
            app_name: アプリ名
            app_features: アプリの特徴
            main_keyword: 主要キーワード
            target_audience: ターゲットユーザー
            
        Returns:
            サブタイトル生成プロンプト
        """
        return cls.get_prompt(
            language=language,
            prompt_type="SUBTITLE_GENERATION",
            app_name=app_name,
            app_features=app_features,
            main_keyword=main_keyword,
            target_audience=target_audience
        )
    
    @classmethod
    def get_description_prompt(cls, language: str, app_name: str, app_features: str,
                              main_keyword: str, related_keywords: str, target_audience: str) -> str:
        """
        概要生成プロンプトを取得
        
        Args:
            language: 言語コード
            app_name: アプリ名
            app_features: アプリの特徴
            main_keyword: 主要キーワード
            related_keywords: 関連キーワード
            target_audience: ターゲットユーザー
            
        Returns:
            概要生成プロンプト
        """
        return cls.get_prompt(
            language=language,
            prompt_type="DESCRIPTION_GENERATION",
            app_name=app_name,
            app_features=app_features,
            main_keyword=main_keyword,
            related_keywords=related_keywords,
            target_audience=target_audience
        )
    
    @classmethod
    def get_title_prompt(cls, language: str, app_info: str, keywords: str) -> str:
        """
        タイトル生成プロンプトを取得
        
        Args:
            language: 言語コード
            app_info: アプリ情報
            keywords: キーワード
            
        Returns:
            タイトル生成プロンプト
        """
        return cls.get_prompt(
            language=language,
            prompt_type="TITLE_GENERATION",
            app_info=app_info,
            keywords=keywords
        )
    
    @classmethod
    def get_keywords_prompt(cls, language: str, keywords: str) -> str:
        """
        キーワード文字列生成プロンプトを取得
        
        Args:
            language: 言語コード
            keywords: キーワード
            
        Returns:
            キーワード文字列生成プロンプト
        """
        return cls.get_prompt(
            language=language,
            prompt_type="KEYWORDS_GENERATION",
            keywords=keywords
        )
    
    @classmethod
    def get_supported_languages(cls) -> list:
        """サポートされている言語のリストを取得"""
        return list(cls.SUPPORTED_LANGUAGES.keys())
    
    @classmethod
    def get_available_prompt_types(cls) -> list:
        """利用可能なプロンプトタイプのリストを取得"""
        # 日本語プロンプトクラスから利用可能なタイプを取得
        return [attr for attr in dir(JapanesePrompts) if not attr.startswith('_')]
