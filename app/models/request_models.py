"""
リクエストモデル
APIリクエストのデータモデル定義
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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
