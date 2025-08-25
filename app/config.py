"""
Application Configuration Settings
"""

import os
from typing import List

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """アプリケーション設定クラス"""

    # プロジェクト基本情報
    PROJECT_NAME: str = "ASO Text Generator API"
    PROJECT_DESCRIPTION: str = "ASO最適化のためのテキスト生成API"
    VERSION: str = "0.1.0"

    # API設定
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 環境設定
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # CORS設定
    ALLOWED_HOSTS: List[str] = ["*"]

    # セキュリティ設定
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 外部API設定
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # データベース設定（将来的に使用）
    DATABASE_URL: str = ""

    # ログ設定
    LOG_LEVEL: str = "INFO"

    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v):
        """CORS設定の検証"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


# グローバル設定インスタンス
settings = Settings()
