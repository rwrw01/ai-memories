"""Shared retry decorator for transient HTTP errors.

Uses tenacity with exponential backoff + jitter.
Only retries on network errors and 5xx status codes — never on 4xx.
"""

import logging

import httpx
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = logging.getLogger(__name__)


def _is_transient(exc: BaseException) -> bool:
    """Return True for errors worth retrying."""
    if isinstance(exc, httpx.RequestError):
        return True
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code >= 500:
        return True
    return False


def _log_retry(state: RetryCallState) -> None:
    """Log each retry attempt."""
    logger.warning(
        "Retry attempt %d for %s: %s",
        state.attempt_number,
        state.fn.__name__ if state.fn else "unknown",
        state.outcome.exception() if state.outcome else "unknown",
    )


service_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception(_is_transient),
    before_sleep=_log_retry,
    reraise=True,
)
