"""
ASO Text Generator API - Main Application Entry Point
"""

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.aso_endpoints import router as aso_router
from app.config import settings
from app.services.aso_text_orchestrator import ASOTextOrchestrator
from app.services.csv_analyzer import CSVAnalyzer
from app.services.description_generator import DescriptionGenerator
from app.services.gemini_generator import GeminiGenerator
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.keyword_selector import KeywordSelector
from app.services.subtitle_generator import SubtitleGenerator
from app.services.title_generator import TitleGenerator
from app.services.whats_new_generator import WhatsNewGenerator
from app.utils.error_handler import (
    aso_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.utils.exceptions import ASOAPIException

# FastAPIアプリケーションの初期化
app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.version,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# エラーハンドラーの登録
app.add_exception_handler(ASOAPIException, aso_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# 依存性注入の設定
def get_csv_analyzer():
    return CSVAnalyzer()


def get_keyword_selector():
    return KeywordSelector()


def get_keyword_field_generator():
    return KeywordFieldGenerator()


def get_title_generator():
    return TitleGenerator()


def get_subtitle_generator():
    gemini_generator = GeminiGenerator()
    return SubtitleGenerator(gemini_generator)


def get_description_generator():
    gemini_generator = GeminiGenerator()
    return DescriptionGenerator(gemini_generator)


def get_whats_new_generator():
    return WhatsNewGenerator()


def get_gemini_generator():
    return GeminiGenerator()


def get_orchestrator():
    return ASOTextOrchestrator()


# APIルーターの登録
app.include_router(aso_router, prefix=settings.api_v1_str, tags=["aso"])


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "ASO Text Generator API",
        "version": settings.version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "service": "ASO Text Generator API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.host, port=settings.port, reload=settings.debug
    )
