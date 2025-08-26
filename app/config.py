"""
Application Configuration Settings
"""

from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Google AI設定
    google_api_key: Optional[str] = None

    # Gemini API設定
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"  # 最新の推奨モデル
    gemini_timeout: int = 30
    gemini_max_retries: int = 3

    # 推奨モデルと許容モデルの定義
    RECOMMENDED_MODELS: List[str] = [
        "gemini-2.5-flash",  # 一般テキスト・マルチモーダル（推奨）
        "gemini-2.5-pro",  # コーディング・複雑な推論（推奨）
    ]

    ACCEPTABLE_MODELS: List[str] = [
        "gemini-2.0-flash",  # 高速処理（許容）
        "gemini-2.0-pro",  # 高精度（許容）
    ]

    # 非推奨モデル（使用禁止）
    DEPRECATED_MODELS: List[str] = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-pro",
    ]

    @property
    def available_models(self) -> List[str]:
        """利用可能なモデルのリストを返す"""
        return self.RECOMMENDED_MODELS + self.ACCEPTABLE_MODELS

    def is_valid_model(self, model_name: str) -> bool:
        """指定されたモデルが有効かどうかをチェック"""
        return model_name in self.available_models

    def get_model_category(self, model_name: str) -> str:
        """モデルのカテゴリを返す"""
        if model_name in self.RECOMMENDED_MODELS:
            return "recommended"
        elif model_name in self.ACCEPTABLE_MODELS:
            return "acceptable"
        elif model_name in self.DEPRECATED_MODELS:
            return "deprecated"
        else:
            return "unknown"

    # アプリケーション設定
    app_name: str = "ASO Text Generator API"
    app_version: str = "1.0.0"
    debug: bool = False

    # FastAPI設定
    project_name: str = "ASO Text Generator API"
    project_description: str = "App Store Optimization用のテキスト生成API"
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"

    # サーバー設定
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS設定
    allowed_hosts: list = ["*"]

    # ログ設定
    log_level: str = "INFO"

    # ファイルアップロード設定
    max_file_size: int = 10485760
    allowed_extensions: str = ".csv"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        json_schema_extra = {
            "example": {
                "google_api_key": "your_google_api_key_here",
                "gemini_api_key": "your_gemini_api_key_here",
                "gemini_model": "gemini-2.5-flash",
                "debug": False,
            }
        }


# グローバル設定インスタンス
settings = Settings()
