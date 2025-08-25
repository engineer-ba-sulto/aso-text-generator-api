"""
ASOエンドポイント
App Store Optimization関連のAPIエンドポイント
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.models.request_models import (
    ASORequest,
    ASOTextGenerationRequest,
    DescriptionRequest,
    SubtitleRequest,
    TitleRequest,
    WhatsNewRequest,
)
from app.models.response_models import (
    ASOResponse,
    ASOTextGenerationResponse,
    DescriptionResponse,
    KeywordFieldResponse,
    SubtitleResponse,
    TitleResponse,
    WhatsNewResponse,
)
from app.services.aso_text_orchestrator import ASOTextOrchestrator
from app.services.csv_analyzer import CSVAnalyzer
from app.services.description_generator import DescriptionGenerator
from app.services.individual_text_orchestrator import IndividualTextOrchestrator
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.keyword_selector import KeywordSelector
from app.services.subtitle_generator import SubtitleGenerator
from app.services.title_generator import TitleGenerator
from app.services.whats_new_generator import WhatsNewGenerator
from app.utils.response_builder import ResponseBuilder

router = APIRouter()


@router.post("/generate-aso-texts", response_model=ASOTextGenerationResponse)
async def generate_aso_texts(
    request: ASOTextGenerationRequest,
    orchestrator: ASOTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
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
            language=request.language,
        )

        # レスポンスの構築
        return response_builder.build_integrated_response(
            keyword_field=result.keyword_field,
            title=result.title,
            subtitle=result.subtitle,
            description=result.description,
            whats_new=result.whats_new,
            language=result.language,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"テキスト生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-keyword-field", response_model=KeywordFieldResponse)
async def generate_keyword_field(
    csv_file: UploadFile = File(...),
    language: str = Form(...),
    csv_analyzer: CSVAnalyzer = Depends(),
    keyword_selector: KeywordSelector = Depends(),
    keyword_field_generator: KeywordFieldGenerator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """
    キーワードフィールド (100文字) を生成するエンドポイント

    - CSVファイルからキーワード分析を実行
    - 主要キーワードを自動選定
    - 指定された言語でキーワードフィールドを生成
    """
    try:
        # 言語パラメータの検証
        if language not in ["ja", "en"]:
            raise HTTPException(
                status_code=400, detail="language must be either 'ja' or 'en'"
            )

        # CSV分析とキーワード選定
        keywords_data = await csv_analyzer.analyze_csv(csv_file)
        primary_keyword = keyword_selector.select_primary_keyword(keywords_data)

        # キーワードフィールド生成
        keyword_field = await keyword_field_generator.generate(
            keywords_data, primary_keyword, language
        )

        # レスポンス構築
        return response_builder.build_keyword_field_response(
            keyword_field=keyword_field, language=language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"キーワードフィールド生成中にエラーが発生しました: {str(e)}",
        )


@router.post("/generate-title", response_model=TitleResponse)
async def generate_title(
    request: TitleRequest,
    title_generator: TitleGenerator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """
    タイトル (30文字) を生成するエンドポイント

    - 主要キーワードとアプリ名からタイトルを生成
    - 指定された言語でタイトルを生成
    """
    try:
        title = await title_generator.generate(
            request.primary_keyword, request.app_name, request.language
        )

        return response_builder.build_title_response(
            title=title, language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"タイトル生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-subtitle", response_model=SubtitleResponse)
async def generate_subtitle(
    request: SubtitleRequest,
    subtitle_generator: SubtitleGenerator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """
    サブタイトル (30文字) を生成するエンドポイント

    - 主要キーワードとアプリの特徴からサブタイトルを生成
    - 指定された言語でサブタイトルを生成
    """
    try:
        subtitle = await subtitle_generator.generate(
            request.primary_keyword, request.features, request.language
        )

        return response_builder.build_subtitle_response(
            subtitle=subtitle, language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"サブタイトル生成中にエラーが発生しました: {str(e)}",
        )


@router.post("/generate-description", response_model=DescriptionResponse)
async def generate_description(
    request: DescriptionRequest,
    description_generator: DescriptionGenerator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """
    概要 (4,000文字) を生成するエンドポイント

    - 主要キーワードとアプリの特徴から概要を生成
    - 指定された言語で概要を生成
    """
    try:
        description = await description_generator.generate(
            request.primary_keyword, request.features, request.language
        )

        return response_builder.build_description_response(
            description=description, language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"概要生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-whats-new", response_model=WhatsNewResponse)
async def generate_whats_new(
    request: WhatsNewRequest,
    whats_new_generator: WhatsNewGenerator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """
    最新情報 (4,000文字) を生成するエンドポイント

    - アプリの特徴から最新情報を生成
    - 指定された言語で最新情報を生成
    """
    try:
        whats_new = await whats_new_generator.generate(
            request.features, request.language
        )

        return response_builder.build_whats_new_response(
            whats_new=whats_new, language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"最新情報生成中にエラーが発生しました: {str(e)}"
        )


# オーケストレーターを使用した個別エンドポイント（効率的な処理フロー版）


@router.post(
    "/generate-keyword-field-orchestrated", response_model=KeywordFieldResponse
)
async def generate_keyword_field_orchestrated(
    csv_file: UploadFile = File(...),
    language: str = Form(...),
    orchestrator: IndividualTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """キーワードフィールド生成エンドポイント（オーケストレーター使用版）"""
    try:
        keyword_field = await orchestrator.generate_keyword_field(csv_file, language)

        return response_builder.build_keyword_field_response(
            keyword_field=keyword_field, language=language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"キーワードフィールド生成中にエラーが発生しました: {str(e)}",
        )


@router.post("/generate-title-orchestrated", response_model=TitleResponse)
async def generate_title_orchestrated(
    request: TitleRequest,
    orchestrator: IndividualTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """タイトル生成エンドポイント（オーケストレーター使用版）"""
    try:
        title = await orchestrator.generate_title(
            request.primary_keyword, request.app_name, request.language
        )

        return response_builder.build_title_response(
            title=title, language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"タイトル生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-subtitle-orchestrated", response_model=SubtitleResponse)
async def generate_subtitle_orchestrated(
    request: SubtitleRequest,
    orchestrator: IndividualTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """サブタイトル生成エンドポイント（オーケストレーター使用版）"""
    try:
        subtitle = await orchestrator.generate_subtitle(
            request.primary_keyword, request.features, request.language
        )

        return response_builder.build_subtitle_response(
            subtitle=subtitle, language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"サブタイトル生成中にエラーが発生しました: {str(e)}",
        )


@router.post("/generate-description-orchestrated", response_model=DescriptionResponse)
async def generate_description_orchestrated(
    request: DescriptionRequest,
    orchestrator: IndividualTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """概要生成エンドポイント（オーケストレーター使用版）"""
    try:
        description = await orchestrator.generate_description(
            request.primary_keyword, request.features, request.language
        )

        return response_builder.build_description_response(
            description=description, language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"概要生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-whats-new-orchestrated", response_model=WhatsNewResponse)
async def generate_whats_new_orchestrated(
    request: WhatsNewRequest,
    orchestrator: IndividualTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
):
    """最新情報生成エンドポイント（オーケストレーター使用版）"""
    try:
        whats_new = await orchestrator.generate_whats_new(
            request.features, request.language
        )

        return response_builder.build_whats_new_response(
            whats_new=whats_new, language=request.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"最新情報生成中にエラーが発生しました: {str(e)}"
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
