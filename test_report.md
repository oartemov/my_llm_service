## 1. Корректный запрос и ответ.

Запрос:
```
curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d "{\"dish\": \"Борщ\", \"output_format\": \"Список + шаги\", \"people\": 4}"
```
Ответ:
```
{{"recipe":"свекла 600 г  \nкартофель 600 г  \nкапуста белокочанная 300 г  \nморковь 150 г  \nлук репчатый 2 шт  \nтоматная паста 3 ст.л  \nмясо говядина 400 г  \nсало-шпик 100 г  \nуксус столовый 9% 1 ст.л \nсахар 1 ч.л  \nчерный перец горошком 5 шт  \nлавровый лист 2 шт  \nсоль по вкусу  \nмолотый черный перец по вкусу  \nчеснок 2 зубчика  \nрастительное масло 50 мл\n\n \n\n1. Мясо промыть, обсушить бумажным полотенцем и нарезать крупными кусками.\n2. Сало-шпик мелко нарезать и обжарить до золотистого цвета на растительном масле.\n3. В сковороду добавить мясо и обжаривать его до румяной корочки.\n4. Добавить нарезанную морковь и лук, перемешать и жарить еще несколько минут.\n5. Свеклу очистить, вымыть и нарезать соломкой или натереть на крупной терке.\n6. Капусту нашинковать тонкой соломкой.\n7. Картофель очистить, помыть и нарезать кубиками среднего размера.\n8. В кастрюлю влить воду, довести до кипения и положить туда подготовленные ингредиенты.","steps":null}
```

## 2. Повторный запрос обращается к кешу (см. cache.jpg).

## 3. Некорретные параметры

Запрос:
```
curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d "{\"dish\": \"xx\", \"output_format\": \"Список + шаги\", \"people\": 4}"
```
Ответ:
```
{"detail":[{"type":"string_too_short","loc":["body","dish"],"msg":"String should have at least 3 characters","input":"xx","ctx":{"min_length":3}}]}
```
Запрос:
```
curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d "{\"dish\": \"Борщ\", \"output_format\": \"Список + шаги\", \"people\": 9}"
```
Ответ:
```
{"detail":[{"type":"less_than_equal","loc":["body","people"],"msg":"Input should be less than or equal to 6","input":9,"ctx":{"le":6}}]}
```
Запрос:
```
curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d "{\"dish\": \"Борщ\", \"output_format\": \"что-то другое\", \"people\": 4}"
```
Ответ:
```
{"detail":[{"type":"literal_error","loc":["body","output_format"],"msg":"Input should be 'Список продуктов' or 'Список + шаги'","input":"что-то другое","ctx":{"expected":"'Список продуктов' or 'Список + шаги'"}}]}
```

## 4. Отключение сети

```
{"detail":"Ошибка подключения: HTTPSConnectionPool(host='ngw.devices.sberbank.ru', port=9443): Max retries exceeded with url: /api/v2/oauth (Caused by NameResolutionError(\"HTTPSConnection(host='ngw.devices.sberbank.ru', port=9443): Failedto resolve 'ngw.devices.sberbank.ru' ([Errno 11001] getaddrinfo failed)\"))"}
```