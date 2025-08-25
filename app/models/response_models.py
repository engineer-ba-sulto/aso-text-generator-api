"""
レスポンスモデル
APIレスポンスのデータモデル定義
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ASOResponse(BaseModel):
    """ASOテキスト生成レスポンスモデル"""
    
    success: bool = Field(..., description="処理成功フラグ")
    generated_text: str = Field(..., description="生成されたテキスト")
    text_type: str = Field(..., description="テキストの種類")
    language: str = Field(..., description="言語")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="メタデータ")


class CSVAnalysisResponse(BaseModel):
    """CSV分析レスポンスモデル"""
    
    success: bool = Field(..., description="処理成功フラグ")
    analysis_result: Dict[str, Any] = Field(..., description="分析結果")
    extracted_keywords: List[str] = Field(..., description="抽出されたキーワード")
    summary: Optional[str] = Field(default=None, description="分析サマリー")


class KeywordSelectionResponse(BaseModel):
    """キーワード選定レスポンスモデル"""
    
    success: bool = Field(..., description="処理成功フラグ")
    selected_keywords: List[str] = Field(..., description="選定されたキーワード")
    priority_scores: Optional[Dict[str, float]] = Field(default=None, description="優先度スコア")
    reasoning: Optional[str] = Field(default=None, description="選定理由")


class ErrorResponse(BaseModel):
    """エラーレスポンスモデル"""
    
    success: bool = Field(default=False, description="処理成功フラグ")
    error_code: str = Field(..., description="エラーコード")
    error_message: str = Field(..., description="エラーメッセージ")
    details: Optional[Dict[str, Any]] = Field(default=None, description="詳細情報")
