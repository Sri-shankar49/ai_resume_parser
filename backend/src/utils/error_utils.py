
# import logging

# logger = logging.getLogger(__name__)


# def log_internal_error(
#     operation: str,
#     exc: Exception,
# ) -> None:
#     # Detailed errors belong in server logs, not API responses.
#     logger.error(
#         "%s failed: %s",
#         operation,
#         type(exc).__name__,
#         exc_info=True,
#     )



import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """An application error safe to map to an HTTP response."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def log_internal_error(operation: str, exc: Exception) -> None:
    """Log technical details internally, not in API responses."""
    logger.error(
        "Operation failed: %s | Error type: %s",
        operation,
        type(exc).__name__,
        exc_info=True,
    )
