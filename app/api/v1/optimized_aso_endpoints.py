from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.models.request_models import (
    DescriptionRequest,
    SubtitleRequest,
    TitleRequest,
    WhatsNewRequest,
)
from app.models.response_models import (
    DescriptionResponse,
    KeywordFieldResponse,
    SubtitleResponse,
    TitleResponse,
    WhatsNewResponse,
)
from app.services.optimized_individual_orchestrator import (
    OptimizedIndividualOrchestrator,
)
from app.utils.flow_logger import FlowLogger
from app.utils.resource_manager import ResourceManager
from app.utils.response_builder import ResponseBuilder

router = APIRouter()


# 最適化されたキーワードフィールド生成エンドポイント
@router.post("/generate-keyword-field", response_model=KeywordFieldResponse)
async def generate_keyword_field_optimized(
    csv_file: UploadFile = File(...),
    language: str = Form(...),
    orchestrator: OptimizedIndividualOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
    resource_manager: ResourceManager = Depends(),
    flow_logger: FlowLogger = Depends(),
):
    """
    最適化されたキーワードフィールド生成エンドポイント
    """
    try:
        # リソース監視開始
        async with resource_manager.resource_monitor():
            # リソース制限チェック
            resource_status = resource_manager.check_resource_limits()
            if resource_status["overloaded"]:
                flow_logger.log_error(
                    "resource_overload", Exception("Resource overload detected")
                )
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable due to high resource usage",
                )

            # キーワードフィールド生成
            keyword_field = await orchestrator.generate_keyword_field_optimized(
                csv_file, language
            )

            # レスポンス構築
            return response_builder.build_keyword_field_response(
                keyword_field=keyword_field, language=language
            )

    except HTTPException:
        raise
    except Exception as e:
        flow_logger.log_error("keyword_field_generation", e)
        raise HTTPException(
            status_code=500,
            detail=f"キーワードフィールド生成中にエラーが発生しました: {str(e)}",
        )


# 最適化されたタイトル生成エンドポイント
@router.post("/generate-title", response_model=TitleResponse)
async def generate_title_optimized(
    request: TitleRequest,
    orchestrator: OptimizedIndividualOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
    resource_manager: ResourceManager = Depends(),
    flow_logger: FlowLogger = Depends(),
):
    """
    最適化されたタイトル生成エンドポイント
    """
    try:
        async with resource_manager.resource_monitor():
            # リソース制限チェック
            resource_status = resource_manager.check_resource_limits()
            if resource_status["overloaded"]:
                flow_logger.log_error(
                    "resource_overload", Exception("Resource overload detected")
                )
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable due to high resource usage",
                )

            # タイトル生成
            title = await orchestrator.generate_title_optimized(
                request.primary_keyword, request.app_name, request.language
            )

            return response_builder.build_title_response(
                title=title, language=request.language
            )

    except HTTPException:
        raise
    except Exception as e:
        flow_logger.log_error("title_generation", e)
        raise HTTPException(
            status_code=500, detail=f"タイトル生成中にエラーが発生しました: {str(e)}"
        )


# 最適化されたサブタイトル生成エンドポイント
@router.post("/generate-subtitle", response_model=SubtitleResponse)
async def generate_subtitle_optimized(
    request: SubtitleRequest,
    orchestrator: OptimizedIndividualOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
    resource_manager: ResourceManager = Depends(),
    flow_logger: FlowLogger = Depends(),
):
    """
    最適化されたサブタイトル生成エンドポイント
    """
    try:
        async with resource_manager.resource_monitor():
            # リソース制限チェック
            resource_status = resource_manager.check_resource_limits()
            if resource_status["overloaded"]:
                flow_logger.log_error(
                    "resource_overload", Exception("Resource overload detected")
                )
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable due to high resource usage",
                )

            # サブタイトル生成
            subtitle = await orchestrator.generate_subtitle_optimized(
                request.primary_keyword, request.features, request.language
            )

            return response_builder.build_subtitle_response(
                subtitle=subtitle, language=request.language
            )

    except HTTPException:
        raise
    except Exception as e:
        flow_logger.log_error("subtitle_generation", e)
        raise HTTPException(
            status_code=500,
            detail=f"サブタイトル生成中にエラーが発生しました: {str(e)}",
        )


# 最適化された概要生成エンドポイント
@router.post("/generate-description", response_model=DescriptionResponse)
async def generate_description_optimized(
    request: DescriptionRequest,
    orchestrator: OptimizedIndividualOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
    resource_manager: ResourceManager = Depends(),
    flow_logger: FlowLogger = Depends(),
):
    """
    最適化された概要生成エンドポイント
    """
    try:
        async with resource_manager.resource_monitor():
            # リソース制限チェック
            resource_status = resource_manager.check_resource_limits()
            if resource_status["overloaded"]:
                flow_logger.log_error(
                    "resource_overload", Exception("Resource overload detected")
                )
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable due to high resource usage",
                )

            # 概要生成
            description = await orchestrator.generate_description_optimized(
                request.primary_keyword, request.features, request.language
            )

            return response_builder.build_description_response(
                description=description, language=request.language
            )

    except HTTPException:
        raise
    except Exception as e:
        flow_logger.log_error("description_generation", e)
        raise HTTPException(
            status_code=500, detail=f"概要生成中にエラーが発生しました: {str(e)}"
        )


# 最適化された最新情報生成エンドポイント
@router.post("/generate-whats-new", response_model=WhatsNewResponse)
async def generate_whats_new_optimized(
    request: WhatsNewRequest,
    orchestrator: OptimizedIndividualOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
    resource_manager: ResourceManager = Depends(),
    flow_logger: FlowLogger = Depends(),
):
    """
    最適化された最新情報生成エンドポイント
    """
    try:
        async with resource_manager.resource_monitor():
            # リソース制限チェック
            resource_status = resource_manager.check_resource_limits()
            if resource_status["overloaded"]:
                flow_logger.log_error(
                    "resource_overload", Exception("Resource overload detected")
                )
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable due to high resource usage",
                )

            # 最新情報生成
            whats_new = await orchestrator.generate_whats_new_optimized(
                request.features, request.language
            )

            return response_builder.build_whats_new_response(
                whats_new=whats_new, language=request.language
            )

    except HTTPException:
        raise
    except Exception as e:
        flow_logger.log_error("whats_new_generation", e)
        raise HTTPException(
            status_code=500, detail=f"最新情報生成中にエラーが発生しました: {str(e)}"
        )
