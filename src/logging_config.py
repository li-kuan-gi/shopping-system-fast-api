import logging
import json
import sys
from datetime import datetime, timezone
from typing_extensions import override
from contextvars import ContextVar

# Context variable to store request-specific information (e.g., correlation ID)
log_context: ContextVar[dict[str, object]] = ContextVar("log_context", default={})


class JSONFormatter(logging.Formatter):
    @override
    def format(self, record: logging.LogRecord) -> str:
        # Base log record
        log_record: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat()
            + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }

        # Merge with context-specific data (like correlation_id)
        context_data = log_context.get()
        if context_data:
            log_record.update(context_data)

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    # Also configure uvicorn/gunicorn loggers
    for name in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "gunicorn.error",
        "gunicorn.access",
    ]:
        log = logging.getLogger(name)
        log.handlers = [handler]
        log.propagate = False
