class AppError(Exception):
    """Base exception for all application errors."""


class NotFoundError(AppError):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, key: str):
        super().__init__(f"'{resource}' not found with key '{key}'")


class ConflictError(AppError):
    """Raised when a resource conflict occurs."""

    def __init__(self, resource: str, key: str):
        super().__init__(f"Conflict with '{resource}' and key '{key}'")


class LLMUnavailableError(AppError):
    """Raised wehn the LLM Provider fails"""
