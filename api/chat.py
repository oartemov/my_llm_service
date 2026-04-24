import time
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional

from services.model import call_llm

from services.logger import (
    setup_logger,
    log_request,
    log_prompt,
    log_response,
    log_error,
    log_timing,
)

logger = setup_logger("chat")
router = APIRouter()

class DishDescription(BaseModel):
    dish: str = Field(..., min_length=3, max_length=100)
    output_format: Literal["Список продуктов", "Список + шаги"]
    people: int = Field(..., ge=1, le=6)


class Recipe(BaseModel):
    recipe: str
    steps: Optional[str] = None

@router.post("/chat", response_model=Recipe)
async def generate_recipe(request: DishDescription) -> Recipe:
    execution_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        log_request(
            logger,
            dish=request.dish,
            people=request.people,
            output_format=request.output_format,
            execution_id=execution_id,
        )

        result = call_llm(
            dish=request.dish,
            people=request.people,
            output_format=request.output_format,
            execution_id=execution_id,
            logger=logger
        )

        response_time = time.time()
        log_response(logger, result, execution_id)
        log_timing(logger, "llm_call", (response_time - start_time) * 1000, execution_id)

        log_timing(logger, "total", (response_time - start_time) * 1000, execution_id)

        return Recipe(recipe=result, steps=None)
    except Exception as e:
        log_error(logger, str(e), execution_id)
        raise HTTPException(status_code=500, detail=str(e))