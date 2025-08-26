"""
レスポンスモデル
APIレスポンスのデータモデル定義
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ASOTextGenerationResponse(BaseModel):
    """
    ASOテキスト生成の統合レスポンスモデル
    """

    # 生成されたテキスト項目
    keyword_field: str = Field(
        ..., description="キーワードフィールド (100文字以内)", max_length=100
    )
    title: str = Field(..., description="アプリタイトル (30文字以内)", max_length=30)
    subtitle: str = Field(..., description="サブタイトル (30文字以内)", max_length=30)
    description: str = Field(
        ..., description="アプリ概要 (4000文字以内)", max_length=4000
    )
    whats_new: str = Field(..., description="最新情報 (4000文字以内)", max_length=4000)

    # メタデータ
    language: str = Field(..., description="生成された言語 (ja: 日本語, en: 英語)")
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, description="生成日時 (UTC)"
    )

    # 処理情報
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        json_schema_extra={
            "example": {
                "keyword_field": "フィットネス トレーニング 健康管理 運動記録",
                "title": "FitTracker - 健康管理アプリ",
                "subtitle": "あなたの健康をサポート",
                "description": "FitTrackerは、あなたの健康管理をサポートする総合的なフィットネスアプリです。...",
                "whats_new": "新機能として、より詳細な運動分析機能を追加しました。...",
                "language": "ja",
                "generated_at": "2024-01-15T10:30:00Z",
                "processing_time": 2.5,
            }
        },
    )


class KeywordFieldResponse(BaseModel):
    """キーワードフィールド生成のレスポンスモデル"""

    keyword_field: str = Field(
        ..., description="キーワードフィールド (100文字以内)", max_length=100
    )
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class TitleResponse(BaseModel):
    """タイトル生成のレスポンスモデル"""

    title: str = Field(..., description="アプリタイトル (30文字以内)", max_length=30)
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class SubtitleResponse(BaseModel):
    """サブタイトル生成のレスポンスモデル"""

    subtitle: str = Field(..., description="サブタイトル (30文字以内)", max_length=30)
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class DescriptionResponse(BaseModel):
    """概要生成のレスポンスモデル"""

    description: str = Field(
        ..., description="アプリ概要 (4000文字以内)", max_length=4000
    )
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class WhatsNewResponse(BaseModel):
    """最新情報生成のレスポンスモデル"""

    whats_new: str = Field(..., description="最新情報 (4000文字以内)", max_length=4000)
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class CSVAnalysisResponse(BaseModel):
    """CSV分析レスポンスモデル"""

    success: bool = Field(..., description="処理成功フラグ")
    data: Dict[str, Any] = Field(..., description="分析結果データ")
    message: str = Field(..., description="処理メッセージ")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


# 既存のモデル（後方互換性のため保持）
class ASOResponse(BaseModel):
    """ASOテキスト生成レスポンスモデル"""

    success: bool = Field(..., description="処理成功フラグ")
    generated_text: str = Field(..., description="生成されたテキスト")
    text_type: str = Field(..., description="テキストの種類")
    language: str = Field(..., description="言語")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="メタデータ")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class KeywordSelectionResponse(BaseModel):
    """キーワード選定レスポンスモデル"""

    success: bool = Field(..., description="処理成功フラグ")
    selected_keywords: List[str] = Field(..., description="選定されたキーワード")
    priority_scores: Optional[Dict[str, float]] = Field(
        default=None, description="優先度スコア"
    )
    reasoning: Optional[str] = Field(default=None, description="選定理由")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


# 新しく追加したモデル（モデル選択機能用）
class ModelsResponse(BaseModel):
    """モデル情報取得レスポンスモデル"""

    recommended_models: List[str] = Field(..., description="推奨モデルリスト")
    acceptable_models: List[str] = Field(..., description="許容モデルリスト")
    current_default: str = Field(..., description="現在のデフォルトモデル")
    model_categories: Dict[str, str] = Field(..., description="モデルカテゴリの説明")
