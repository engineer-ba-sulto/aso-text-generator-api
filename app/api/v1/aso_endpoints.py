"""
ASOエンドポイント
App Store Optimization関連のAPIエンドポイント
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.config import settings
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
    CSVAnalysisResponse,
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


# 依存性注入のファクトリ関数
def get_aso_text_orchestrator() -> ASOTextOrchestrator:
    return ASOTextOrchestrator()


def get_csv_analyzer() -> CSVAnalyzer:
    return CSVAnalyzer()


def get_keyword_selector() -> KeywordSelector:
    return KeywordSelector()


def get_keyword_field_generator() -> KeywordFieldGenerator:
    return KeywordFieldGenerator()


def get_title_generator() -> TitleGenerator:
    return TitleGenerator()


def get_subtitle_generator() -> SubtitleGenerator:
    from app.services.gemini_generator import GeminiGenerator

    gemini_generator = GeminiGenerator()
    return SubtitleGenerator(gemini_generator)


def get_description_generator() -> DescriptionGenerator:
    from app.services.gemini_generator import GeminiGenerator

    gemini_generator = GeminiGenerator()
    return DescriptionGenerator(gemini_generator)


def create_gemini_generator(model_name: str = None) -> GeminiGenerator:
    """指定されたモデルでGeminiGeneratorを作成"""
    from app.services.gemini_generator import GeminiGenerator

    return GeminiGenerator(model_name=model_name)


def get_whats_new_generator() -> WhatsNewGenerator:
    return WhatsNewGenerator()


def get_response_builder() -> ResponseBuilder:
    return ResponseBuilder()


def get_individual_text_orchestrator() -> IndividualTextOrchestrator:
    return IndividualTextOrchestrator()


@router.get("/models", response_model=Dict[str, List[str]])
async def get_available_models():
    """
    利用可能なGeminiモデルの一覧を取得するエンドポイント

    Returns:
        推奨モデルと許容モデルのリスト
    """
    return {
        "recommended_models": settings.RECOMMENDED_MODELS,
        "acceptable_models": settings.ACCEPTABLE_MODELS,
        "current_default": settings.gemini_model,
        "model_categories": {
            "recommended": "最新の推奨モデル（最高性能）",
            "acceptable": "許容モデル（明示的に要求された場合のみ使用）",
            "deprecated": "非推奨モデル（使用禁止）",
        },
    }


@router.post("/generate-aso-texts", response_model=ASOTextGenerationResponse)
async def generate_aso_texts(
    request: ASOTextGenerationRequest,
    orchestrator: ASOTextOrchestrator = Depends(get_aso_text_orchestrator),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    csv_analyzer: CSVAnalyzer = Depends(get_csv_analyzer),
    keyword_selector: KeywordSelector = Depends(get_keyword_selector),
    keyword_field_generator: KeywordFieldGenerator = Depends(
        get_keyword_field_generator
    ),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    title_generator: TitleGenerator = Depends(get_title_generator),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    subtitle_generator: SubtitleGenerator = Depends(get_subtitle_generator),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    description_generator: DescriptionGenerator = Depends(get_description_generator),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    whats_new_generator: WhatsNewGenerator = Depends(get_whats_new_generator),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    orchestrator: IndividualTextOrchestrator = Depends(
        get_individual_text_orchestrator
    ),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    orchestrator: IndividualTextOrchestrator = Depends(
        get_individual_text_orchestrator
    ),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    orchestrator: IndividualTextOrchestrator = Depends(
        get_individual_text_orchestrator
    ),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    orchestrator: IndividualTextOrchestrator = Depends(
        get_individual_text_orchestrator
    ),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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
    orchestrator: IndividualTextOrchestrator = Depends(
        get_individual_text_orchestrator
    ),
    response_builder: ResponseBuilder = Depends(get_response_builder),
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


@router.post("/analyze-csv", response_model=CSVAnalysisResponse)
async def analyze_csv(
    file: UploadFile = File(...),
    csv_analyzer: CSVAnalyzer = Depends(get_csv_analyzer),
):
    """
    CSVファイルを分析するエンドポイント

    Args:
        file: アップロードされたCSVファイル

    Returns:
        分析結果
    """
    try:
        # ファイル拡張子の確認
        if not file.filename.endswith(".csv"):
            raise HTTPException(
                status_code=400, detail="CSVファイルのみアップロード可能です"
            )

        # 一時ファイルとして保存
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # CSV分析を実行
            analysis_result = csv_analyzer.analyze_csv(temp_file_path)

            return CSVAnalysisResponse(
                success=True, data=analysis_result, message="CSV分析が完了しました"
            )

        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"CSV分析中にエラーが発生しました: {str(e)}"
        )


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
