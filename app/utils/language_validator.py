"""
言語パラメータの検証と管理
"""

from typing import Literal
from pydantic import validator

LanguageType = Literal['ja', 'en']


class LanguageValidator:
    """言語パラメータの検証と管理"""
    
    SUPPORTED_LANGUAGES = ['ja', 'en']
    
    @classmethod
    def validate_language(cls, language: str) -> LanguageType:
        """
        言語パラメータを検証
        
        Args:
            language: 検証する言語パラメータ
            
        Returns:
            LanguageType: 検証済みの言語パラメータ
            
        Raises:
            ValueError: 無効な言語パラメータの場合
        """
        if language not in cls.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported languages: {cls.SUPPORTED_LANGUAGES}"
            )
        return language
    
    @classmethod
    def get_language_name(cls, language: LanguageType) -> str:
        """
        言語コードから言語名を取得
        
        Args:
            language: 言語コード
            
        Returns:
            str: 言語名
        """
        language_names = {
            'ja': '日本語',
            'en': 'English'
        }
        return language_names.get(language, language)
    
    @classmethod
    def is_supported(cls, language: str) -> bool:
        """
        言語がサポートされているかチェック
        
        Args:
            language: チェックする言語
            
        Returns:
            bool: サポートされている場合True
        """
        return language in cls.SUPPORTED_LANGUAGES
