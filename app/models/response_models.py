"""
レスポンスモデル
APIレスポンスのデータモデル定義
"""

from datetime import datetime
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


class KeywordFieldResponse(BaseModel):
    """キーワードフィールド生成レスポンスモデル"""
    
    success: bool = Field(..., description="処理成功フラグ")
    keyword_field: str = Field(..., description="生成されたキーワードフィールド")
    length: int = Field(..., description="キーワードフィールドの文字数")
    primary_keyword: str = Field(..., description="主要キーワード")
    language: str = Field(..., description="言語")
    generated_at: str = Field(..., description="生成日時")


class TitleResponse(BaseModel):
    """タイトル生成レスポンスモデル"""
    
    success: bool = Field(..., description="処理成功フラグ")
    title: str = Field(..., description="生成されたタイトル")
    length: int = Field(..., description="タイトルの文字数")
    primary_keyword: str = Field(..., description="主要キーワード")
    app_base_name: str = Field(..., description="アプリ基本名")
    language: str = Field(..., description="言語")
    generated_at: str = Field(..., description="生成日時")


class WhatsNewResponse(BaseModel):
    """最新情報生成レスポンスモデル"""
    
    success: bool = Field(..., description="処理成功フラグ")
    whats_new: str = Field(..., description="生成された最新情報")
    length: int = Field(..., description="最新情報の文字数")
    primary_keyword: str = Field(..., description="主要キーワード")
    keyword_occurrences: int = Field(..., description="キーワード出現回数")
    language: str = Field(..., description="言語")
    generated_at: str = Field(..., description="生成日時")


class ASOTextGenerationResponse(BaseModel):
    """統合ASOテキスト生成レスポンスモデル"""
    
    keyword_field: str = Field(..., description="キーワードフィールド (100文字)")
    title: str = Field(..., description="タイトル (30文字)")
    subtitle: str = Field(..., description="サブタイトル (30文字)")
    description: str = Field(..., description="概要 (4000文字)")
    whats_new: str = Field(..., description="最新情報 (4000文字)")
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """エラーレスポンスモデル"""
    
    success: bool = Field(default=False, description="処理成功フラグ")
    error_code: str = Field(..., description="エラーコード")
    error_message: str = Field(..., description="エラーメッセージ")
    details: Optional[Dict[str, Any]] = Field(default=None, description="詳細情報")
