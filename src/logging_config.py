import logging
import json
import sys
from datetime import datetime, timezone
from typing_extensions import override

class JSONFormatter(logging.Formatter):
    @override
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
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
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access", "gunicorn.error", "gunicorn.access"]:
        log = logging.getLogger(name)
        log.handlers = [handler]
        log.propagate = False
