import logging
from datetime import datetime

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.models.error_models import ErrorResponse
from app.utils.exceptions import ASOAPIException

logger = logging.getLogger(__name__)


async def aso_exception_handler(request: Request, exc: ASOAPIException):
    error_response = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        timestamp=datetime.utcnow(),
        path=request.url.path,
    )
    logger.error(f"ASO API Error: {exc.error_code} - {exc.message}")
    return JSONResponse(status_code=exc.status_code, content=error_response.dict())


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_response = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details=exc.errors(),
        timestamp=datetime.utcnow(),
        path=request.url.path,
    )
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    error_response = ErrorResponse(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        timestamp=datetime.utcnow(),
        path=request.url.path,
    )
    logger.error(f"Unexpected Error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response.dict()
    )
