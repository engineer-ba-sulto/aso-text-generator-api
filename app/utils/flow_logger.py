"""
処理フローのログ記録
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime


class FlowLogger:
    """処理フローのログ記録"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = None
        self.step_times = {}
    
    def log_flow_start(self, language: str, app_name: str):
        """処理フロー開始のログ"""
        self.start_time = time.time()
        self.logger.info(
            f"ASO text generation flow started - Language: {language}, App: {app_name}"
        )
    
    def log_step_completion(self, step_name: str, duration: float):
        """ステップ完了のログ"""
        self.step_times[step_name] = duration
        self.logger.info(f"Step '{step_name}' completed in {duration:.2f}s")
    
    def log_flow_completion(self, total_duration: float):
        """処理フロー完了のログ"""
        self.logger.info(f"ASO text generation flow completed in {total_duration:.2f}s")
        
        # 各ステップの詳細ログ
        if self.step_times:
            self.logger.info("Step breakdown:")
            for step_name, duration in self.step_times.items():
                percentage = (duration / total_duration) * 100
                self.logger.info(f"  {step_name}: {duration:.2f}s ({percentage:.1f}%)")
    
    def log_error(self, step_name: str, error: Exception):
        """エラーのログ"""
        self.logger.error(f"Error in step '{step_name}': {str(error)}")
    
    def log_warning(self, step_name: str, message: str):
        """警告のログ"""
        self.logger.warning(f"Warning in step '{step_name}': {message}")
    
    def log_info(self, step_name: str, message: str):
        """情報のログ"""
        self.logger.info(f"Info in step '{step_name}': {message}")
    
    def reset_timer(self):
        """タイマーをリセット"""
        self.start_time = None
        self.step_times = {}
