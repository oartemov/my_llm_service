# Recipe Generator API

Генерация списка продуктов и рецептов для приготовления блюд.

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

Создайте `config/config.yaml` с вашими учетными данными GigaChat:

```yaml
gigachat:
  auth_url: "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
  api_url: "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
  credentials: ""  # GIGACHAT_CREDENTIALS (Base64)
  api_key: ""      # GIGACHAT_API_KEY (Bearer token)
```

Или используйте переменные окружения:
- `GIGACHAT_CREDENTIALS`
- `GIGACHAT_API_KEY`

## Запуск

```bash
uvicorn main:app --reload
```

API доступно по адресу: http://localhost:8000

Документация Swagger: http://localhost:8000/docs

## Эндпоинт

### POST /api/chat

Генерация списка продуктов и шагов приготовления.

**Параметры запроса:**

| Параметр | Тип | Обязательно | Описание |
|---------|-----|------------|----------|
| dish | string | Да | Название блюда (3-100 символов) |
| output_format | string | Да | "Список продуктов" или "Список + шаги" |
| people | integer | Да | Количество персон (1-6) |

**Пример запроса:**

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"dish": "Борщ", "output_format": "Список + шаги", "people": 4}'
```

**Пример ответа (200 OK):**

```json
{
  "recipe": "- картофель 500 г\n- свекла 300 г\n- морковь 200 г\n- лук 200 г\n- капуста 500 г\n- говядина 700 г\n- томатная паста 3 ст.л.\n- уксус 2 ст.л.\n- соль, перец по вкусу",
  "steps": "1. Нарезать говядину и варить бульон.\n2. Нарезать овощи.\n3. Обжарить лук и морковь.\n4. Добавить свеклу с уксусом.\n5. Соединить с бульоном.\n6. Добавить капусту и картофель.\n7. Варить до готовности.\n8. Дать настояться."
}
```

**Ошибки:**

- `422 Unprocessable Entity` — ошибка валидации входных данных
- `500 Internal Server Error` — ошибка при вызове LLM

## Логи

Логи сохраняются в каталоге `log/`.

## Кеш

Результаты кешируются в каталоге `cache/`. TTL — 10 минут.

## Тесты

```bash
pytest tests/
```

Тесты покрывают:
- Валидный запрос → успешный ответ (200 OK)
- Ошибки валидации (dish 3-100 символов, people 1-6, output_format)
- Сбой внешнего вызова → ошибка 500
- Повторный запрос → cache hit (быстрый ответ)

## Структура проекта

```
.
├── api/
│   └── chat.py       # Эндпоинт     
├── cache/            # Файловый кеш
├── config/
│   └── config.yaml   # Конфигурация
├── log/              # Логи
├── llm/
│   └── llm.py        # GigaChat API
├── services/
│   ├── model.py      # Обёртка над LLM
│   ├── file_cache.py # Функции работы с кешем
│   └── logger.py     # Логирование
├── main.py           # Точка входа
└── requirements.txt
```