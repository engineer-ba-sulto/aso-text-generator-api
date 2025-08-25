from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: Optional[Any] = None
    timestamp: datetime
    path: str
