### チケット: P0-005 エラーハンドリング

#### 背景 / 目的

- **背景**: プロジェクト基盤は整備済みだが、一貫したエラーレスポンス形式とグローバルエラーハンドリングが未実装
- **目的**: グローバルエラーハンドラーを実装し、一貫したエラーレスポンス形式を定義して、API の信頼性と保守性を向上させる

#### スコープ（このチケットでやること）

- **カスタム例外クラスの定義**

  ```python
  # app/utils/exceptions.py
  class ASOAPIException(Exception):
      def __init__(self, message: str, error_code: str, status_code: int = 400):
          self.message = message
          self.error_code = error_code
          self.status_code = status_code
          super().__init__(self.message)

  class CSVValidationError(ASOAPIException):
      def __init__(self, message: str):
          super().__init__(message, "CSV_VALIDATION_ERROR", 400)

  class KeywordSelectionError(ASOAPIException):
      def __init__(self, message: str):
          super().__init__(message, "KEYWORD_SELECTION_ERROR", 400)

  class TextGenerationError(ASOAPIException):
      def __init__(self, message: str):
          super().__init__(message, "TEXT_GENERATION_ERROR", 500)

  class GeminiAPIError(ASOAPIException):
      def __init__(self, message: str):
          super().__init__(message, "GEMINI_API_ERROR", 503)
  ```

- **エラーレスポンスモデルの定義**

  ```python
  # app/models/error_models.py
  from pydantic import BaseModel
  from typing import Optional, Any
  from datetime import datetime

  class ErrorResponse(BaseModel):
      success: bool = False
      error_code: str
      message: str
      details: Optional[Any] = None
      timestamp: datetime
      path: str
  ```

- **グローバルエラーハンドラーの実装**

  ```python
  # app/utils/error_handler.py
  from fastapi import Request, status
  from fastapi.responses import JSONResponse
  from fastapi.exceptions import RequestValidationError
  from app.utils.exceptions import ASOAPIException
  from app.models.error_models import ErrorResponse
  from datetime import datetime
  import logging

  logger = logging.getLogger(__name__)

  async def aso_exception_handler(request: Request, exc: ASOAPIException):
      error_response = ErrorResponse(
          error_code=exc.error_code,
          message=exc.message,
          timestamp=datetime.utcnow(),
          path=request.url.path
      )
      logger.error(f"ASO API Error: {exc.error_code} - {exc.message}")
      return JSONResponse(
          status_code=exc.status_code,
          content=error_response.dict()
      )

  async def validation_exception_handler(request: Request, exc: RequestValidationError):
      error_response = ErrorResponse(
          error_code="VALIDATION_ERROR",
          message="Request validation failed",
          details=exc.errors(),
          timestamp=datetime.utcnow(),
          path=request.url.path
      )
      logger.error(f"Validation Error: {exc.errors()}")
      return JSONResponse(
          status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
          content=error_response.dict()
      )

  async def general_exception_handler(request: Request, exc: Exception):
      error_response = ErrorResponse(
          error_code="INTERNAL_SERVER_ERROR",
          message="An unexpected error occurred",
          timestamp=datetime.utcnow(),
          path=request.url.path
      )
      logger.error(f"Unexpected Error: {str(exc)}", exc_info=True)
      return JSONResponse(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          content=error_response.dict()
      )
  ```

- **エラーハンドラーの登録**

  ```python
  # app/main.py
  from fastapi import FastAPI
  from app.utils.error_handler import (
      aso_exception_handler,
      validation_exception_handler,
      general_exception_handler
  )
  from app.utils.exceptions import ASOAPIException
  from fastapi.exceptions import RequestValidationError

  app = FastAPI()

  # エラーハンドラーの登録
  app.add_exception_handler(ASOAPIException, aso_exception_handler)
  app.add_exception_handler(RequestValidationError, validation_exception_handler)
  app.add_exception_handler(Exception, general_exception_handler)
  ```

#### やらないこと（Out of Scope）

- 各サービスクラスの実装（STEP1 以降で対応）
- 具体的なビジネスロジックのエラーハンドリング（各ステップで対応）
- ログ出力の詳細設定（必要に応じて後で調整）

#### 受入条件（Acceptance Criteria）

- カスタム例外クラスが定義されていること
- エラーレスポンスモデルが実装されていること
- グローバルエラーハンドラーが実装されていること
- エラーハンドラーが FastAPI アプリケーションに登録されていること
- エラーログが適切に出力されること
- 一貫したエラーレスポンス形式が保証されていること

#### 影響/変更ファイル

- 追加:
  - `app/utils/exceptions.py`
  - `app/models/error_models.py`
  - `app/utils/error_handler.py`
- 変更:
  - `app/main.py`（エラーハンドラーの登録）

#### 依存関係 / ブロッカー

- P0-001（プロジェクト初期化）の完了が必要
- P0-002（依存関係管理）の完了が必要
- P0-003（プロジェクト構造）の完了が必要
- P0-004（環境設定）の完了が必要

#### 参考資料

- `docs/MVP開発ロードマップ.md` の「ステップ 0：プロジェクト基盤の構築」
- [FastAPI エラーハンドリング](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Python 例外処理](https://docs.python.org/3/tutorial/errors.html)
- [ログ出力ベストプラクティス](https://docs.python.org/3/howto/logging.html)

#### リスク / 留意点

- エラーコードの体系的な管理
- セキュリティを考慮したエラーメッセージ
- ログ出力の適切な設定
- エラーレスポンスの国際化対応

#### 見積り

- 2 時間（計画準拠）
