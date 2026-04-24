import time
from llm.llm import GigaChatClient
from services.file_cache import get_from_cache, save_to_cache
from services.logger import (
    setup_logger,
    log_request,
    log_prompt,
    log_response,
    log_error,
    log_timing,
)

def build_prompt(dish: str, people: int, output_format: str) -> str:
    if output_format == "Список продуктов":
        format_instruction = """
        Верни ТОЛЬКО список покупок (каждый продукт с новой строки).
        Без лишних комментариев, приветствий и пояснений.
        Используй маркированный список с дефисами (- продукт количество).
        Пример:
        - картофель 1 кг
        - лук репчатый 2 шт
        - соль по вкусу
        """
    else:
        format_instruction = """
        Сначала верни список покупок (каждый продукт с новой строки, с дефисами).
        Затем через пустую строку верни короткие шаги приготовления (5-8 пунктов, каждый с новой строки с цифрами).
        Пример:
        - картофель 1 кг
        - лук репчатый 2 шт
        
        1. Очистить и нарезать картофель.
        2. Обжарить лук.
        ...
        """

    return f"""Блюдо: {dish}
Количество персон: {people}

{format_instruction}"""

def call_llm(dish: str, people: int, output_format: str, execution_id: str, logger) -> str:
    start_time = time.time()

    cached_result, is_hit = get_from_cache(
        dish=dish,
        people=people,
        output_format=output_format
    )
    if is_hit:
        return cached_result

    client = GigaChatClient()
    prompt = build_prompt(
        dish=dish,
        people=people,
        output_format=output_format
    )

    generate_time = time.time()
    log_prompt(logger, prompt, execution_id)
    log_timing(logger, "prompt_generation", (generate_time - start_time) * 1000, execution_id)

    result, error = client.generate_shopping_list(prompt)

    if error:
        log_error(logger, error, execution_id)
        raise Exception(error)

    save_to_cache(
        dish=dish,
        people=people,
        output_format=output_format,
        result=result
    )

    return result

