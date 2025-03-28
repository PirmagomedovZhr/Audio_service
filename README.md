# Audio Service with Yandex OAuth

Сервис для загрузки аудио-файлов от пользователей с возможностью авторизации через Яндекс и выпуском внутренних JWT-токенов.

---

## Оглавление

1. [Описание проекта](#описание-проекта)  
2. [Технологии и стек](#технологии-и-стек)  
3. [Структура проекта](#структура-проекта)  
4. [Настройка и запуск](#настройка-и-запуск)  
   - [Переменные окружения (.env)](#переменные-окружения-env)  
   - [Docker и docker-compose](#docker-и-docker-compose)  
   - [Быстрый старт](#быстрый-старт)  
5. [Использование API](#использование-api)  
   - [Авторизация через Яндекс](#авторизация-через-яндекс)  
   - [JWT-токены (login, refresh)](#jwt-токены-login-refresh)  
   - [Управление пользователями](#управление-пользователями)  
   - [Управление аудиофайлами](#управление-аудиофайлами)  
6. [Проверка выполнения требований](#проверка-выполнения-требований)

---

## Описание проекта

Данное приложение позволяет пользователям:

- Авторизоваться через [Яндекс OAuth](https://oauth.yandex.ru/)  
- Получать внутренний **JWT**-токен для аутентификации при дальнейших запросах  
- Загружать аудиофайлы (хранятся **локально** в папке `uploads`)  
- Суперпользователям — удалять других пользователей  

Приложение написано на **FastAPI**, использует **SQLAlchemy (async)** и базу данных **PostgreSQL 16**. Развёртывание реализовано с помощью **Docker** (docker-compose).

---

## Технологии и стек

- **Python 3.10**  
- **FastAPI** — асинхронный веб-фреймворк  
- **SQLAlchemy Async** — ORM для PostgreSQL  
- **Uvicorn** — ASGI-сервер  
- **Docker / docker-compose** — контейнеризация  
- **PostgreSQL 16** — СУБД  
- **JWT (PyJWT)** — внутренняя аутентификация  
- **Pydantic** — валидация данных  
- **python-dotenv** — чтение переменных окружения  
- **email-validator** — поддержка `EmailStr`  
- **httpx** — запросы к Яндекс OAuth

---

## Структура проекта

```bash
.
├── .env                 # Переменные окружения (НЕ пушить в публичный репозиторий!)
├── docker-compose.yml   # Описание сервисов (PostgreSQL + FastAPI-приложение)
├── Dockerfile           # Сборка Docker-образа приложения
├── README.md            # Документация (текущий файл)
├── requirements.txt     # Список зависимостей Python
├── app                  # Папка с исходным кодом приложения
│   ├── __init__.py
│   ├── config.py        # Чтение env-переменных (Pydantic Settings)
│   ├── database.py      # Инициализация AsyncSession для PostgreSQL
│   ├── main.py          # Точка входа (FastAPI-приложение)
│   ├── models.py        # SQLAlchemy-модели (User, AudioFile)
│   ├── oauth.py         # Авторизация через Яндекс (эндпоинты /auth/yandex/*)
│   ├── schemas.py       # Pydantic-схемы (User, Token, AudioFile и т.д.)
│   ├── security.py      # JWT-логика (create_access_token, decode_token)
│   ├── services.py      # CRUD, загрузка файлов и др.
│   └── utils.py         # Утилиты (хэширование паролей, валидация)
└── uploads              # Папка для загружаемых аудиофайлов
```

---

## Настройка и запуск

### Переменные окружения (.env)

Пример файла `.env`:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=audio_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

YANDEX_CLIENT_ID=your_client_id
YANDEX_CLIENT_SECRET=your_client_secret
YANDEX_REDIRECT_URI=http://localhost:8000/auth/yandex/callback

JWT_SECRET=supersecretkey
JWT_ALGORITHM=HS256

DEBUG=true
```

Замените значения на свои. Файл `.env` не должен попадать в публичный репозиторий!

### Docker и docker-compose

- **Dockerfile**: сборка образа Python 3.10, установка зависимостей и запуск через Uvicorn.
- **docker-compose.yml**: содержит сервисы PostgreSQL и приложение FastAPI.

### Быстрый старт


Создайте `.env` (пример выше) и запустите приложение:

```bash
docker-compose up --build
```

Приложение доступно: [http://localhost:8000](http://localhost:8000)

Документация Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)  
Документация ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Использование API

Подробности — в документации (`/docs`).

### Авторизация через Яндекс

- `GET /auth/yandex/login`: получение ссылки для авторизации
- `GET /auth/yandex/callback`: обмен кода авторизации на внутренний JWT

### JWT-токены (login, refresh)

- `POST /login`: авторизация через email/password, возвращает JWT
- `POST /refresh_token`: обновление JWT-токена

### Управление пользователями

- `POST /users`: создать пользователя
- `GET /users/me`: текущий пользователь
- `PATCH /users/me`: обновить профиль
- `DELETE /users/{user_id}`: удалить пользователя (только суперпользователь)

### Управление аудиофайлами

- `POST /upload`: загрузить файл
- `GET /my_files`: список загруженных файлов

---

## Проверка выполнения требований

- [x] FastAPI, SQLAlchemy (async), Docker
- [x] PostgreSQL 16
- [x] Локальное хранение файлов
- [x] Асинхронный код
- [x] Яндекс OAuth
- [x] JWT-токены
- [x] Полная документация
