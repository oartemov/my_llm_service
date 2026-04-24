import logging
import json
import time
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "log"


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data)


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        log_file = LOG_DIR / f"{name}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


def log_request(logger, dish: str, people: int, output_format: str, execution_id: str):
    logger.info(
        "Incoming request",
        extra={
            "event": "request_received",
            "dish": dish,
            "people": people,
            "output_format": output_format,
            "execution_id": execution_id,
        },
    )


def log_prompt(logger, prompt: str, execution_id: str):
    logger.info(
        "Prompt generated",
        extra={
            "event": "prompt_generated",
            "prompt": prompt,
            "execution_id": execution_id,
        },
    )


def log_response(logger, response: str, execution_id: str):
    logger.info(
        "Model response received",
        extra={
            "event": "model_response",
            "response": response,
            "execution_id": execution_id,
        },
    )


def log_error(logger, error: str, execution_id: str):
    logger.error(
        "Error occurred",
        extra={
            "event": "error",
            "error": error,
            "execution_id": execution_id,
        },
    )


def log_timing(logger, stage: str, duration_ms: float, execution_id: str):
    logger.info(
        f"Stage completed",
        extra={
            "event": "timing",
            "stage": stage,
            "duration_ms": duration_ms,
            "execution_id": execution_id,
        },
    )