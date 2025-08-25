"""
ASOエンドポイント
App Store Optimization関連のAPIエンドポイント
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.models.request_models import ASORequest, ASOTextGenerationRequest
from app.models.response_models import ASOResponse, ASOTextGenerationResponse
from app.services.csv_analyzer import CSVAnalyzer
from app.services.description_generator import DescriptionGenerator
from app.services.gemini_generator import GeminiGenerator
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.keyword_selector import KeywordSelector
from app.services.subtitle_generator import SubtitleGenerator
from app.services.title_generator import TitleGenerator
from app.services.whats_new_generator import WhatsNewGenerator

router = APIRouter()


@router.post("/generate-aso-texts", response_model=ASOTextGenerationResponse)
async def generate_aso_texts(
    request: ASOTextGenerationRequest,
    csv_analyzer: CSVAnalyzer = Depends(),
    keyword_selector: KeywordSelector = Depends(),
    keyword_field_generator: KeywordFieldGenerator = Depends(),
    title_generator: TitleGenerator = Depends(),
    subtitle_generator: SubtitleGenerator = Depends(),
    description_generator: DescriptionGenerator = Depends(),
    whats_new_generator: WhatsNewGenerator = Depends(),
    gemini_generator: GeminiGenerator = Depends(),
):
    """
    ASOテキストを一括生成するエンドポイント

    - CSVファイルからキーワード分析を実行
    - 主要キーワードを自動選定
    - 指定された言語で全テキスト項目を生成
    """
    try:
        # 1. CSV分析とキーワード選定
        keywords_data = await csv_analyzer.analyze_csv(request.csv_file)
        primary_keyword = keyword_selector.select_primary_keyword(keywords_data)

        # 2. 各テキスト項目の生成（言語パラメータを引き渡し）
        keyword_field = keyword_field_generator.generate(
            keywords_data, primary_keyword, request.language
        )
        title = title_generator.generate(
            primary_keyword, request.app_name, request.language
        )
        subtitle = subtitle_generator.generate(
            primary_keyword, request.features, request.language
        )
        description = description_generator.generate(
            primary_keyword, request.features, request.language
        )
        whats_new = whats_new_generator.generate(request.features, request.language)

        # 3. レスポンスの構築
        return ASOTextGenerationResponse(
            keyword_field=keyword_field,
            title=title,
            subtitle=subtitle,
            description=description,
            whats_new=whats_new,
            language=request.language,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"テキスト生成中にエラーが発生しました: {str(e)}"
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
