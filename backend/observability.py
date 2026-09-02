"""Structured JSON logging + request-context middleware.

Emits one JSON log line per HTTP request to stdout. On ECS / App Runner /
Lambda the platform ships stdout to CloudWatch Logs automatically, so no
boto3 or agent is required. In CloudWatch Logs Insights you can then filter
by ``request_id``, ``status`` or ``latency_ms`` (see docs/QA_AWS_RUNBOOK.md).

Stdlib only — nothing to add to requirements.txt.
"""
from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

REQUEST_ID_HEADER = "x-request-id"
SLOW_REQUEST_MS = 1000.0
_LOGGER_NAME = "shoeshub"

logger = logging.getLogger(_LOGGER_NAME)


class JsonFormatter(logging.Formatter):
    """Render each log record as a single line of JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(getattr(record, "extra_fields", {}))
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Attach a single stdout JSON handler to the app logger (idempotent)."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    logger.propagate = False


def log_event(message: str, /, level: int = logging.INFO, **fields: Any) -> None:
    """Emit a structured log line carrying arbitrary key/value fields."""
    logger.log(level, message, extra={"extra_fields": fields})


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assign a request id, time the request, log one JSON line per response."""

    def __init__(self, app: ASGIApp, *, slow_ms: float = SLOW_REQUEST_MS) -> None:
        super().__init__(app)
        self._slow_ms = slow_ms

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            log_event(
                "request_failed",
                level=logging.ERROR,
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
            )
            raise
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        log_event(
            "request",
            level=logging.WARNING if latency_ms >= self._slow_ms else logging.INFO,
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            latency_ms=latency_ms,
        )
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
