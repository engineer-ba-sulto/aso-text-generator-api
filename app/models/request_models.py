"""
リクエストモデル
APIリクエストのデータモデル定義
"""

from typing import Any, Dict, List, Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field, validator


class ASOTextGenerationRequest(BaseModel):
    """統合ASOテキスト生成リクエストモデル"""

    csv_file: UploadFile
    app_name: str
    features: List[str]
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v


class KeywordFieldRequest(BaseModel):
    """キーワードフィールド生成リクエストモデル"""
    
    keywords_data: Dict[str, Any] = Field(..., description="キーワードデータ")
    primary_keyword: str = Field(..., description="主要キーワード")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v


class TitleRequest(BaseModel):
    """タイトル生成リクエストモデル"""
    
    app_name: str = Field(..., description="アプリ名")
    primary_keyword: str = Field(..., description="主要キーワード")
    features: List[str] = Field(..., description="アプリ機能")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v


class SubtitleRequest(BaseModel):
    """サブタイトル生成リクエストモデル"""
    
    app_name: str = Field(..., description="アプリ名")
    primary_keyword: str = Field(..., description="主要キーワード")
    features: List[str] = Field(..., description="アプリ機能")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v


class DescriptionRequest(BaseModel):
    """概要生成リクエストモデル"""
    
    app_name: str = Field(..., description="アプリ名")
    primary_keyword: str = Field(..., description="主要キーワード")
    features: List[str] = Field(..., description="アプリ機能")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v


class WhatsNewRequest(BaseModel):
    """最新情報生成リクエストモデル"""
    
    app_name: str = Field(..., description="アプリ名")
    primary_keyword: str = Field(..., description="主要キーワード")
    features: List[str] = Field(..., description="アプリ機能")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v


class ASORequest(BaseModel):
    """ASOテキスト生成リクエストモデル"""

    app_name: str = Field(..., description="アプリ名")
    app_description: str = Field(..., description="アプリの説明")
    keywords: List[str] = Field(..., description="キーワードのリスト")
    target_language: str = Field(default="ja", description="ターゲット言語")
    text_type: str = Field(
        ..., description="生成するテキストの種類（title, description, keywords）"
    )
    additional_info: Optional[Dict[str, Any]] = Field(
        default=None, description="追加情報"
    )


class CSVAnalysisRequest(BaseModel):
    """CSV分析リクエストモデル"""

    file_path: str = Field(..., description="CSVファイルのパス")
    analysis_type: str = Field(default="keywords", description="分析タイプ")
    parameters: Optional[Dict[str, Any]] = Field(
        default=None, description="分析パラメータ"
    )


class KeywordSelectionRequest(BaseModel):
    """キーワード選定リクエストモデル"""

    keywords: List[str] = Field(..., description="候補キーワードのリスト")
    target_count: int = Field(default=10, description="選定するキーワード数")
    selection_criteria: Optional[Dict[str, Any]] = Field(
        default=None, description="選定基準"
    )
