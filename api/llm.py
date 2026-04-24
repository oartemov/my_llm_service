from llm.llm import GigaChatClient
from cache.file_cache import get_from_cache, save_to_cache


def call_llm(dish: str, people: int, output_format: str) -> str:
    cached_result, is_hit = get_from_cache(
        dish=dish,
        people=people,
        output_format=output_format
    )
    if is_hit:
        return cached_result

    client = GigaChatClient()
    result, error = client.generate_shopping_list(
        dish=dish,
        people=people,
        output_format=output_format
    )
    if error:
        raise Exception(error)

    save_to_cache(
        dish=dish,
        people=people,
        output_format=output_format,
        result=result
    )
    return result