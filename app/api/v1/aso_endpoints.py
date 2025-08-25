"""
ASOエンドポイント
App Store Optimization関連のAPIエンドポイント
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.models.request_models import (
    ASORequest, 
    ASOTextGenerationRequest,
    KeywordFieldRequest,
    TitleRequest,
    SubtitleRequest,
    DescriptionRequest,
    WhatsNewRequest
)
from app.models.response_models import (
    ASOResponse, 
    ASOTextGenerationResponse,
    KeywordFieldResponse,
    TitleResponse,
    SubtitleResponse,
    DescriptionResponse,
    WhatsNewResponse
)
from app.services.aso_text_orchestrator import ASOTextOrchestrator
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.title_generator import TitleGenerator
from app.services.subtitle_generator import SubtitleGenerator
from app.services.description_generator import DescriptionGenerator
from app.services.whats_new_generator import WhatsNewGenerator
from app.utils.response_builder import ResponseBuilder

router = APIRouter()


@router.post("/generate-aso-texts", response_model=ASOTextGenerationResponse)
async def generate_aso_texts(
    request: ASOTextGenerationRequest,
    orchestrator: ASOTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """
    ASOテキストを一括生成するエンドポイント
    
    - CSVファイルからキーワード分析を実行
    - 主要キーワードを自動選定
    - 指定された言語で全テキスト項目を生成
    """
    try:
        # テキスト生成の実行
        result = await orchestrator.generate_all_texts(
            csv_file=request.csv_file,
            app_name=request.app_name,
            features=request.features,
            language=request.language
        )
        
        # レスポンスの構築
        return response_builder.build_integrated_response(
            keyword_field=result.keyword_field,
            title=result.title,
            subtitle=result.subtitle,
            description=result.description,
            whats_new=result.whats_new,
            language=result.language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"テキスト生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-keyword-field", response_model=KeywordFieldResponse)
async def generate_keyword_field(
    request: KeywordFieldRequest,
    keyword_field_generator: KeywordFieldGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """キーワードフィールド生成エンドポイント"""
    try:
        keyword_field = await keyword_field_generator.generate(
            request.keywords_data,
            request.primary_keyword,
            request.language
        )
        
        return response_builder.build_keyword_field_response(
            keyword_field=keyword_field,
            language=request.language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"キーワードフィールド生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-title", response_model=TitleResponse)
async def generate_title(
    request: TitleRequest,
    title_generator: TitleGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """タイトル生成エンドポイント"""
    try:
        title = await title_generator.generate(
            request.app_name,
            request.primary_keyword,
            request.features,
            request.language
        )
        
        return response_builder.build_title_response(
            title=title,
            language=request.language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"タイトル生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-subtitle", response_model=SubtitleResponse)
async def generate_subtitle(
    request: SubtitleRequest,
    subtitle_generator: SubtitleGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """サブタイトル生成エンドポイント"""
    try:
        subtitle = await subtitle_generator.generate(
            request.app_name,
            request.primary_keyword,
            request.features,
            request.language
        )
        
        return response_builder.build_subtitle_response(
            subtitle=subtitle,
            language=request.language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"サブタイトル生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-description", response_model=DescriptionResponse)
async def generate_description(
    request: DescriptionRequest,
    description_generator: DescriptionGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """概要生成エンドポイント"""
    try:
        description = await description_generator.generate(
            request.app_name,
            request.primary_keyword,
            request.features,
            request.language
        )
        
        return response_builder.build_description_response(
            description=description,
            language=request.language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"概要生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-whats-new", response_model=WhatsNewResponse)
async def generate_whats_new(
    request: WhatsNewRequest,
    whats_new_generator: WhatsNewGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """最新情報生成エンドポイント"""
    try:
        whats_new = await whats_new_generator.generate(
            request.app_name,
            request.primary_keyword,
            request.features,
            request.language
        )
        
        return response_builder.build_whats_new_response(
            whats_new=whats_new,
            language=request.language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"最新情報生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/analyze-csv", response_model=Dict[str, Any])
async def analyze_csv(file: UploadFile = File(...)):
    """
    CSVファイルを分析するエンドポイント

    Args:
        file: アップロードされたCSVファイル

    Returns:
        分析結果
    """
    pass


@router.post("/generate-text", response_model=ASOResponse)
async def generate_text(request: ASORequest):
    """
    ASOテキストを生成するエンドポイント

    Args:
        request: テキスト生成リクエスト

    Returns:
        生成されたASOテキスト
    """
    pass


@router.post("/select-keywords", response_model=List[str])
async def select_keywords(keywords: List[str], target_count: int = 10):
    """
    キーワードを選定するエンドポイント

    Args:
        keywords: 候補キーワードのリスト
        target_count: 選定するキーワード数

    Returns:
        選定されたキーワードのリスト
    """
    pass
