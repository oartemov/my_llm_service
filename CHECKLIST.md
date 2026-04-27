# Чек-лист самопроверки

## Тестирование и самопроверка

### Основные сценарии
- [ ] Корректный запрос → успешный ответ (200 OK)
- [ ] Некорректный ввод → ошибка валидации (422)
- [ ] Сбой внешнего вызова → fallback (500)

### Инфраструктура
- [ ] Сервис запускается одной командой (`uvicorn main:app --reload`)
- [ ] CI проходит успешно (lint, test, build)
- [ ] Конфигурации работают корректно (config.yaml)

### Проверка вручную

```bash
# Запуск сервиса
uvicorn main:app --reload

# Тест 1: Валидный запрос
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"dish": "Борщ", "output_format": "Список + шаги", "people": 4}'
# Ожидается: 200 OK с recipe и steps

# Тест 2: Некорректный ввод (dish < 3 символа)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"dish": "Бо", "output_format": "Список", "people": 2}'
# Ожидается: 422 Unprocessable Entity

# Тест 3: Некорректный ввод (people > 6)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"dish": "Борщ", "output_format": "Список", "people": 10}'
# Ожидается: 422 Unprocessable Entity

# Тест 4: Повторный запрос (проверка кеша)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"dish": "Пельмени", "output_format": "Список", "people": 2}'
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"dish": "Пельмени", "output_format": "Список", "people": 2}'
# Ожидается: второй запрос быстрее (cache hit)

# Тест 5: Запуск тестов
pytest tests/ -v
# Ожидается: All tests passed
```

---

## 9. Проверка CI/CD

```bash
# Проверка синтаксиса
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Проверка установки зависимостей
pip install -r requirements.txt
python -c "from main import app; print('OK')"
```