import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional, Tuple

CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_TTL_SECONDS = 600  # 10 minutes
logger = logging.getLogger("chat")


def _get_cache_dir() -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_DIR


def _generate_cache_key(
    dish: str,
    people: int,
    output_format: str,
    model: str = "GigaChat",
    temperature: float = 0.7,
    system_prompt: str = "Ты помощник."
) -> str:
    data = f"{dish}|{people}|{output_format}|{model}|{temperature}|{system_prompt}"
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _get_cache_path(key: str) -> Path:
    return _get_cache_dir() / f"{key}.json"


def get_from_cache(
    dish: str,
    people: int,
    output_format: str,
    model: str = "GigaChat",
    temperature: float = 0.7,
    system_prompt: str = "Ты помощник."
) -> Tuple[Optional[str], bool]:
    """
    Returns (cached_result, is_hit).
    """
    key = _generate_cache_key(dish, people, output_format, model, temperature, system_prompt)
    cache_path = _get_cache_path(key)

    if not cache_path.exists():
        logger.info("Cache miss", extra={"event": "cache_miss", "key": key[:16] + "..."})
        return None, False

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        cached_at = cache_data.get("cached_at", 0)
        if time.time() - cached_at > CACHE_TTL_SECONDS:
            logger.info("Cache expired", extra={"event": "cache_expired", "key": key[:16] + "..."})
            return None, False

        result = cache_data.get("result")
        logger.info("Cache hit", extra={"event": "cache_hit", "key": key[:16] + "..."})
        return result, True

    except Exception:
        return None, False


def save_to_cache(
    dish: str,
    people: int,
    output_format: str,
    result: str,
    model: str = "GigaChat",
    temperature: float = 0.7,
    system_prompt: str = "Ты помощник."
) -> None:
    key = _generate_cache_key(dish, people, output_format, model, temperature, system_prompt)
    cache_path = _get_cache_path(key)

    cache_data = {
        "dish": dish,
        "people": people,
        "output_format": output_format,
        "model": model,
        "temperature": temperature,
        "system_prompt": system_prompt,
        "result": result,
        "cached_at": time.time()
    }

    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        logger.info("Cache saved", extra={"event": "cache_saved", "key": key[:16] + "..."})
    except Exception as e:
        logger.warning(f"Failed to save cache: {e}")