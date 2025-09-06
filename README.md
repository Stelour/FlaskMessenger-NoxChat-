# NoxChat — Flask Messenger

## Описание

NoxChat — это мини‑социальный сервис на Flask.

---

## Навыки и цели проекта

- Архитектура Flask через фабрику приложения и Blueprints (auth/main/errors).
- Современный SQLAlchemy 2.x: типизированные модели (`Mapped`), связи many‑to‑many, ассоциативные таблицы.
- Поиск: Полнотекстовый при помощи Elasticsearch.
- Работа с медиа: безопасная загрузка аватаров, EXIF‑поворот, crop‑to‑square, resize до 256×256 (Pillow).
- Аутентификация и безопасность: Flask‑Login, CSRF (Flask‑WTF), JWT‑токены сброса пароля (PyJWT), хеширование (Werkzeug).
- UI‑паттерны: пагинация и AJAX‑подгрузка, Jinja2 шаблоны, Flask‑Moment для времени.
- Операционка: конфигурация через `.env`, ротация логов, изолированные почтовые отправки (Flask‑Mail + поток).

---

## Возможности

- Регистрация и вход: по email или Public ID, запоминание сессии (Flask‑Login).
- Профиль: имя пользователя, Bio, Public ID; загрузка аватара с авто‑кропом до 256×256, безопасные имена, очистка старых файлов; перенос папки аватара при смене Public ID.
- Друзья: заявки (отправка/принятие/отклонение/отмена), добавление/удаление из друзей, счётчики входящих/исходящих/друзей, списки «Друзья», «Исходящие», «Входящие» с поиском.
- Поиск пользователей: по имени пользователя или Public ID и AJAX‑подгрузка (инфинит‑скролл).
- Email: сброс пароля по email с JWT‑токеном, асинхронная отправка писем (Flask‑Mail + поток).
- Логи: запись в `logs/noxchat.log`.
- Поиск: интеграция с Elasticsearch для индексации `User`/`Profile`.

---

## Технологии

- Flask 3.x (Blueprints, фабрика `create_app`), Jinja2, Flask‑Moment
- Flask‑Login (сессии, `@login_required`), Flask‑WTF (формы, CSRF)
- Flask‑SQLAlchemy 3.x на базе SQLAlchemy 2.x (типизированные `Mapped`, отношения, селекты 2.0)
- Alembic (каталог `migrations/`)
- Flask‑Mail + поток (асинхронная отправка писем)
- PyJWT (JWT‑токены для сброса пароля)
- Pillow (EXIF transpose, crop, resize)
- Elasticsearch (опционально) через `app/search.py`
- python‑dotenv (переменные окружения)

---

## Архитектура

- Blueprints: `auth`, `main`, `errors`
- Модели: `User`, `Profile`, таблицы `friends` и `friend_requests`
- Сервис поиска: `app/search.py` + `SearchableMixin`
- Утилиты для аватаров: `app/main/avatar_utils.py`

---

## Практики и безопасность

- Пароли: хеширование (Werkzeug), проверка без хранения оригинала
- CSRF в формах (Flask‑WTF), `login_required` на приватных маршрутах
- JWT‑токены сброса пароля с TTL
- Логи продакшена: `logs/noxchat.log` с ротацией

---

## Требования

- Python 3.10+
- Доступ к PostgreSQL
- Рекомендуется виртуальное окружение (`venv`)

---

## Установка

1) Клонируйте репозиторий и создайте окружение:

   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`

2) Создайте `.env` в корне проекта (см. раздел «Конфигурация» ниже).

3) Примените миграции базы данных:
   - `flask --app main db upgrade`

4) (Опционально) поднимите dev SMTP для отладки писем:
   - `aiosmtpd -n -c aiosmtpd.handlers.Debugging -l localhost:8025`

---

## Конфигурация

Основные переменные окружения (.env):

- `SECRET_KEY` — секретный ключ Flask
- `SQLALCHEMY_DATABASE_URI` — строка подключения к БД
- `MAIL_SERVER`, `MAIL_PORT` — SMTP для отправки писем (для разработки можно локальный сервер)
- `ELASTICSEARCH_URL` — URL Elasticsearch

Пример `.env`:

```env
SECRET_KEY=change-me
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://user:pass@localhost/noxchat
MAIL_SERVER=localhost
MAIL_PORT=8025
ELASTICSEARCH_URL=http://localhost:9200
```

---

## Миграции БД

- Создать миграцию: `flask --app main db migrate -m "message"`
- Применить миграции: `flask --app main db upgrade`
- Полная инициализация (если миграций ещё нет):
  - `flask --app main db init`
  - `flask --app main db migrate -m "init"`
  - `flask --app main db upgrade`

---

## Запуск

- Разработка: `flask --app main run --debug`

---

## Структура проекта

- `main.py` — точка входа и shell‑контекст (`main:app`)
- `app/__init__.py` — фабрика приложения, Blueprints, логирование, Elasticsearch
- `app/models.py` — модели `User`, `Profile`, дружба и заявки, JWT‑токены сброса пароля
- `app/main/*` — маршруты, формы, утилиты (аватары, список обновлений)
- `app/auth/*` — аутентификация, регистрация, сброс пароля и email‑шаблоны
- `app/templates/*` — Jinja2 шаблоны
- `app/static/*` — стили, изображения, аватары
- `migrations/` — Alembic миграции
- `config.py` — загрузка `.env`, основные настройки
