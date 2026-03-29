"""
utils/error_handler.py
Centralised error handling utilities for the Object Life pipeline.
"""

import time
import functools
import traceback
from utils.logger import get_logger

logger = get_logger(__name__)


class UploadError(Exception):
    """Raised when an upload to any platform fails after all retries."""
    def __init__(self, platform: str, reason: str):
        self.platform = platform
        self.reason = reason
        super().__init__(f"[{platform.upper()}] {reason}")


class AuthenticationError(Exception):
    """Raised when authentication to a platform fails."""


def retry(max_attempts: int = 3, delay: float = 2.0, backoff: float = 2.0, exceptions=(Exception,)):
    """
    Decorator: retry the wrapped function up to *max_attempts* times.
    Each retry waits *delay* seconds, multiplied by *backoff* on every failure.

    Usage:
        @retry(max_attempts=3, delay=2, exceptions=(requests.Timeout,))
        def upload(...):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_attempts:
                        logger.error(
                            f"❌ '{func.__name__}' failed after {max_attempts} attempts: {exc}"
                        )
                        raise
                    logger.warning(
                        f"⚠️ '{func.__name__}' attempt {attempt}/{max_attempts} failed: {exc}. "
                        f"Retrying in {wait:.1f}s..."
                    )
                    time.sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator


def safe_upload(platform: str):
    """
    Decorator: catch all exceptions from an upload method, log them,
    and return None instead of crashing the whole pipeline.

    Usage:
        @safe_upload("facebook")
        def upload_video(self, ...):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                logger.error(
                    f"💥 Unhandled error in {platform} uploader — {func.__name__}: {exc}\n"
                    + traceback.format_exc()
                )
                return None
        return wrapper
    return decorator


def log_pipeline_step(step_name: str):
    """
    Decorator: log entry and exit of a major pipeline step.

    Usage:
        @log_pipeline_step("YouTube Upload")
        def upload_video(self, ...):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"▶️  Starting: {step_name}")
            result = func(*args, **kwargs)
            status = "✅ Done" if result else "❌ Failed"
            logger.info(f"{status}: {step_name}")
            return result
        return wrapper
    return decorator
