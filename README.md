FastAPI Glossary (Глоссарий)

Описание
- Простое API на FastAPI для управления глоссарием терминов про распознавание шаблонов проектирования.
- Поддерживаются операции CRUD: список терминов, получение по keyword, добавление, обновление, удаление.
- Данные хранятся в SQLite (файл glossary.db в корне контейнера/проекта).
- Автоматическое создание таблиц и начальное наполнение 10 терминами при старте приложения.
- Документация OpenAPI доступна по /docs (Swagger UI) и /redoc.

Запуск локально
1) Установите зависимости:
   pip install -r requirements.txt
2) Запустите приложение:
   uvicorn app.main:app --reload
3) Откройте http://127.0.0.1:8000/ (произойдет редирект на /docs).

Docker
- Собрать образ и запустить:
  docker build -t glossary-api .
  docker run -p 8000:8000 --name glossary_api glossary-api

Docker Compose
- Либо одной командой:
  docker compose up --build

API
- Список терминов: GET /terms
- Получить термин: GET /terms/{keyword}
- Создать: POST /terms
  Пример тела:
  {
    "keyword": "observer",
    "title": "Наблюдатель",
    "description": "Поведенческий паттерн..."
  }
- Обновить: PUT /terms/{keyword}
  Тело (любые поля title/description):
  { "title": "..." }
- Удалить: DELETE /terms/{keyword}

Заметки
- Поле keyword уникально.
- Валидация запросов выполняется через Pydantic-схемы.
- Авто-миграция реализована через Base.metadata.create_all() при старте приложения.
