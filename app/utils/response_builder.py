"""
レスポンスビルダー
APIレスポンスの構築を担当するユーティリティクラス
"""

from typing import Dict, Any, Optional
from datetime import datetime
import time
from app.models.response_models import (
    ASOTextGenerationResponse,
    KeywordFieldResponse,
    TitleResponse,
    SubtitleResponse,
    DescriptionResponse,
    WhatsNewResponse
)

class ResponseBuilder:
    """レスポンス構築のユーティリティクラス"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def build_integrated_response(
        self,
        keyword_field: str,
        title: str,
        subtitle: str,
        description: str,
        whats_new: str,
        language: str
    ) -> ASOTextGenerationResponse:
        """
        統合レスポンスを構築
        
        Args:
            keyword_field: キーワードフィールド
            title: タイトル
            subtitle: サブタイトル
            description: 概要
            whats_new: 最新情報
            language: 生成言語
            
        Returns:
            ASOTextGenerationResponse: 統合レスポンス
        """
        processing_time = time.time() - self.start_time
        
        return ASOTextGenerationResponse(
            keyword_field=keyword_field,
            title=title,
            subtitle=subtitle,
            description=description,
            whats_new=whats_new,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_keyword_field_response(
        self,
        keyword_field: str,
        language: str
    ) -> KeywordFieldResponse:
        """キーワードフィールドレスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return KeywordFieldResponse(
            keyword_field=keyword_field,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_title_response(
        self,
        title: str,
        language: str
    ) -> TitleResponse:
        """タイトルレスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return TitleResponse(
            title=title,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_subtitle_response(
        self,
        subtitle: str,
        language: str
    ) -> SubtitleResponse:
        """サブタイトルレスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return SubtitleResponse(
            subtitle=subtitle,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_description_response(
        self,
        description: str,
        language: str
    ) -> DescriptionResponse:
        """概要レスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return DescriptionResponse(
            description=description,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_whats_new_response(
        self,
        whats_new: str,
        language: str
    ) -> WhatsNewResponse:
        """最新情報レスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return WhatsNewResponse(
            whats_new=whats_new,
            language=language,
            processing_time=round(processing_time, 2)
        )
