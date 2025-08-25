"""
Application Configuration Settings
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Google AI設定
    google_api_key: Optional[str] = None

    # Gemini API設定
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-pro"
    gemini_timeout: int = 30
    gemini_max_retries: int = 3

    # アプリケーション設定
    app_name: str = "ASO Text Generator API"
    app_version: str = "1.0.0"
    debug: bool = False

    # サーバー設定
    host: str = "0.0.0.0"
    port: int = 8000

    # ログ設定
    log_level: str = "INFO"

    # ファイルアップロード設定
    max_file_size: int = 10485760
    allowed_extensions: str = ".csv"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# グローバル設定インスタンス
settings = Settings()
