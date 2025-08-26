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
    model_name: Optional[str] = Field(
        None,
        description="使用するGeminiモデル名（指定しない場合は設定ファイルのデフォルトを使用）",
    )

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v

    @validator("model_name")
    def validate_model_name(cls, v):
        if v is not None:
            from app.config import settings

            if not settings.is_valid_model(v):
                category = settings.get_model_category(v)
                if category == "deprecated":
                    raise ValueError(
                        f"非推奨モデル '{v}' は使用できません。"
                        f"推奨モデル: {settings.RECOMMENDED_MODELS}, "
                        f"許容モデル: {settings.ACCEPTABLE_MODELS}"
                    )
                else:
                    raise ValueError(
                        f"無効なモデル '{v}' が指定されました。"
                        f"利用可能なモデル: {settings.available_models}"
                    )
        return v


class KeywordFieldRequest(BaseModel):
    """キーワードフィールド生成のリクエストモデル"""

    csv_file: UploadFile
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v


class TitleRequest(BaseModel):
    """タイトル生成のリクエストモデル"""

    primary_keyword: str = Field(..., description="主要キーワード")
    app_name: str = Field(..., description="アプリ名")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v


class SubtitleRequest(BaseModel):
    """サブタイトル生成のリクエストモデル"""

    primary_keyword: str = Field(..., description="主要キーワード")
    features: List[str] = Field(..., description="アプリの特徴リスト")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")
    model_name: Optional[str] = Field(
        None,
        description="使用するGeminiモデル名（指定しない場合は設定ファイルのデフォルトを使用）",
    )

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v

    @validator("model_name")
    def validate_model_name(cls, v):
        if v is not None:
            from app.config import settings

            if not settings.is_valid_model(v):
                category = settings.get_model_category(v)
                if category == "deprecated":
                    raise ValueError(
                        f"非推奨モデル '{v}' は使用できません。"
                        f"推奨モデル: {settings.RECOMMENDED_MODELS}, "
                        f"許容モデル: {settings.ACCEPTABLE_MODELS}"
                    )
                else:
                    raise ValueError(
                        f"無効なモデル '{v}' が指定されました。"
                        f"利用可能なモデル: {settings.available_models}"
                    )
        return v


class DescriptionRequest(BaseModel):
    """概要生成のリクエストモデル"""

    primary_keyword: str = Field(..., description="主要キーワード")
    features: List[str] = Field(..., description="アプリの特徴リスト")
    language: str = Field(..., description="生成言語を指定 (ja: 日本語, en: 英語)")
    model_name: Optional[str] = Field(
        None,
        description="使用するGeminiモデル名（指定しない場合は設定ファイルのデフォルトを使用）",
    )

    @validator("language")
    def validate_language(cls, v):
        if v not in ["ja", "en"]:
            raise ValueError('language must be either "ja" or "en"')
        return v

    @validator("model_name")
    def validate_model_name(cls, v):
        if v is not None:
            from app.config import settings

            if not settings.is_valid_model(v):
                category = settings.get_model_category(v)
                if category == "deprecated":
                    raise ValueError(
                        f"非推奨モデル '{v}' は使用できません。"
                        f"推奨モデル: {settings.RECOMMENDED_MODELS}, "
                        f"許容モデル: {settings.ACCEPTABLE_MODELS}"
                    )
                else:
                    raise ValueError(
                        f"無効なモデル '{v}' が指定されました。"
                        f"利用可能なモデル: {settings.available_models}"
                    )
        return v


class WhatsNewRequest(BaseModel):
    """最新情報生成のリクエストモデル"""

    features: List[str] = Field(..., description="アプリの特徴リスト")
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
