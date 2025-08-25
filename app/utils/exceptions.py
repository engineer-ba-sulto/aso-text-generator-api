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
