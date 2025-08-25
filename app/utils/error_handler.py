"""
エラーハンドラー
アプリケーション全体のエラー処理を管理
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class ErrorHandler:
    """エラーハンドラークラス"""
    
    def __init__(self):
        """初期化"""
        pass
    
    @staticmethod
    def handle_csv_error(error: Exception, file_path: str) -> Dict[str, Any]:
        """
        CSV処理エラーをハンドルする
        
        Args:
            error: 発生したエラー
            file_path: ファイルパス
            
        Returns:
            エラー情報の辞書
        """
        logger.error(f"CSV processing error for {file_path}: {str(error)}")
        return {
            "error_type": "csv_processing_error",
            "message": f"CSVファイルの処理中にエラーが発生しました: {str(error)}",
            "file_path": file_path
        }
    
    @staticmethod
    def handle_api_error(error: Exception, endpoint: str) -> Dict[str, Any]:
        """
        APIエラーをハンドルする
        
        Args:
            error: 発生したエラー
            endpoint: エンドポイント名
            
        Returns:
            エラー情報の辞書
        """
        logger.error(f"API error in {endpoint}: {str(error)}")
        return {
            "error_type": "api_error",
            "message": f"API処理中にエラーが発生しました: {str(error)}",
            "endpoint": endpoint
        }
    
    @staticmethod
    def handle_generation_error(error: Exception, text_type: str) -> Dict[str, Any]:
        """
        テキスト生成エラーをハンドルする
        
        Args:
            error: 発生したエラー
            text_type: テキストタイプ
            
        Returns:
            エラー情報の辞書
        """
        logger.error(f"Text generation error for {text_type}: {str(error)}")
        return {
            "error_type": "generation_error",
            "message": f"テキスト生成中にエラーが発生しました: {str(error)}",
            "text_type": text_type
        }
