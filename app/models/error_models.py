from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    エラーレスポンスの統一モデル
    """

    error: str = Field(..., description="エラーメッセージ")
    error_code: str = Field(..., description="エラーコード")
    detail: Optional[str] = Field(None, description="詳細なエラー情報")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = Field(None, description="エラーが発生したエンドポイント")

    class Config:
        schema_extra = {
            "example": {
                "error": "Invalid language parameter",
                "error_code": "INVALID_LANGUAGE",
                "detail": "Language must be either 'ja' or 'en'",
                "timestamp": "2024-01-15T10:30:00Z",
                "path": "/api/v1/generate-aso-texts",
            }
        }


class ValidationErrorResponse(BaseModel):
    """
    バリデーションエラーのレスポンスモデル
    """

    error: str = Field(default="Validation Error", description="エラーメッセージ")
    error_code: str = Field(default="VALIDATION_ERROR", description="エラーコード")
    validation_errors: Dict[str, Any] = Field(
        ..., description="バリデーションエラーの詳細"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# 後方互換性のため保持
class LegacyErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: Optional[Any] = None
    timestamp: datetime
    path: str
