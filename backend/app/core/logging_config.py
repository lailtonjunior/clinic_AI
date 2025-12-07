import json
import logging
from datetime import datetime


class JSONRequestFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("path", "method", "status_code", "duration_ms", "tenant_id", "user_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=True)


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JSONRequestFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
