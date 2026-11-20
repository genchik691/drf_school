# drf_school — DRF-проект

Django + Django REST Framework: веб-школа с курсами и уроками, кастомный пользователь с авторизацией по email, JWT, права доступа по ролям и платежи.

---

## 📌 О проекте

Учебный проект по Django REST Framework. Реализованы модели курсов, уроков и платежей, кастомный пользователь, JWT-аутентификация, разграничение прав (пользователь / модератор) и фильтрация платежей.

---

## 🛠 Технологии

| Технология | Версия | Назначение |
|:-----------|:------:|:-----------|
| Python | 3.10+ | Язык программирования |
| Django | 4.2+ | Веб-фреймворк |
| Django REST Framework | 3.15+ | REST API |
| SimpleJWT | 5.3+ | JWT-аутентификация |
| django-filter | 24.3+ | Фильтрация |
| drf-spectacular | 0.28+ | OpenAPI / Swagger |
| Celery | 5.3+ | Фоновые задачи |
| Redis | 5.0+ | Брокер и result backend |
| python-dotenv | 1.0+ | Переменные окружения |
| django-celery-beat | 2.5+ | Расписание задач (опционально) |
| Stripe | 7.0+ | Платёжный шлюз |
| Pillow | 11.0+ | Работа с изображениями |
| SQLite | 3 | База данных (разработка) |

---

## 📂 Структура проекта
````
drf_school/
├── manage.py
├── requirements.txt
├── .env.example # Пример переменных (без секретов)
├── .gitignore # Исключает .env, db.sqlite3, media/, schema.yml
├── README.md
│
├── drf_school/ # Настройки проекта
│ ├── init.py
│ ├── celery.py # Celery instance + beat_schedule
│ ├── settings.py # JWT, DRF, AUTH_USER_MODEL, Celery
│ ├── urls.py
│ ├── wsgi.py
│ └── asgi.py
│
├── users/ # Приложение "Пользователи"
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py # User, Payment
│ ├── managers.py # UserManager
│ ├── serializers.py # UserProfile, UserRegister, Payment
│ ├── views.py # Register, UserViewSet, Profile, Payments, Stripe
│ ├── tasks.py # deactivate_inactive_users
│ ├── permissions.py # IsModerator, IsOwnerOrModerator
│ ├── filters.py # PaymentFilter
│ ├── urls.py
│ ├── fixtures/
│ │ ├── payments.json
│ │ └── groups.json
│ ├── management/
│ │ └── commands/
│ │ └── load_payments.py
│ └── migrations/
│
├── lms/ # Приложение "Курсы и уроки"
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py # Course, Lesson, Subscription
│ ├── serializers.py # Course, Lesson
│ ├── views.py # CourseViewSet, Lesson Generic, Subscription
│ ├── tasks.py # send_course_update_email
│ ├── services.py # Stripe helpers
│ ├── urls.py
│ └── migrations/
│
└── media/ # Загруженные файлы
├── avatars/
├── courses/
└── lessons/
````


---

## 🌐 Эндпоинты

### 🔐 Аутентификация (открыты)

| Метод | URL | Назначение |
|:------|:----|:-----------|
| `POST` | `/register/` | Регистрация пользователя |
| `POST` | `/token/` | Получить `access` + `refresh` |
| `POST` | `/token/refresh/` | Обновить `access` |

### 👤 Пользователи

| Метод | URL | Доступ |
|:------|:----|:------:|
| `GET` | `/users/` | 🔒 |
| `POST` | `/users/` | 🔒 |
| `GET` | `/users/<id>/` | 🔒 |
| `PUT/PATCH` | `/users/<id>/` | 🔒 |
| `DELETE` | `/users/<id>/` | 🔒 |
| `GET` | `/users/profile/` | 🔒 (свой) |
| `PATCH` | `/users/profile/` | 🔒 (свой) |

### 📚 Курсы

| Метод | URL | Доступ |
|:------|:----|:------:|
| `GET` | `/courses/` | 🔒 (свои / модератор — все) |
| `POST` | `/courses/` | 🔒 (не модератор) |
| `GET` | `/courses/<id>/` | 🔒 (свой / модератор) |
| `PUT/PATCH` | `/courses/<id>/` | 🔒 (владелец / модератор) |
| `DELETE` | `/courses/<id>/` | 🔒 (не модератор) |

### 📖 Уроки

| Метод | URL | Доступ |
|:------|:----|:------:|
| `GET` | `/lessons/` | 🔒 (свои / модератор — все) |
| `POST` | `/lessons/` | 🔒 (не модератор) |
| `GET` | `/lessons/<id>/` | 🔒 (свой / модератор) |
| `PUT/PATCH` | `/lessons/<id>/` | 🔒 (владелец / модератор) |
| `DELETE` | `/lessons/<id>/` | 🔒 (не модератор) |

### 🔔 Подписка

| Метод | URL | Доступ |
|:------|:----|:------:|
| `POST` | `/subscriptions/` | 🔒 (toggle: создаёт или удаляет подписку на курс) |


### 💳 Платежи

| Метод | URL | Доступ |
|:------|:----|:------:|
| `GET` | `/payments/` | 🔒 (только свои) |
| `POST` | `/payments/create/` | 🔒 (создать Stripe Checkout Session) |
| `GET` | `/payments/status/<session_id>/` | 🔒 (проверить статус, синхронизирует БД) |
| `GET` | `/payments/success/` | 🔓 (редирект Stripe) |
| `GET` | `/payments/cancel/` | 🔓 (редирект Stripe) |

### 📘 Документация

| URL | Назначение |
|:----|:-----------|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI-схема (YAML) |


### 🔍 Фильтры платежей

| Параметр | Пример | Назначение |
|:---------|:-------|:-----------|
| `ordering` | `?ordering=payment_date` | Сортировка по возрастанию |
| `ordering` | `?ordering=-payment_date` | Сортировка по убыванию |
| `course` | `?course=1` | Фильтр по курсу |
| `lesson` | `?lesson=1` | Фильтр по уроку |
| `payment_method` | `?payment_method=cash` | Наличные / перевод |

> 🔒 — только для авторизованных (JWT `Authorization: Bearer <access>`)

---

## 📋 Модели данных

### 👤 User (Пользователь)

| Поле | Тип | Описание |
|:-----|:----|:---------|
| `email` | `EmailField` | Email (уникальный, `USERNAME_FIELD`) |
| `password` | `CharField` | Пароль (хэшируется) |
| `phone` | `CharField` | Телефон |
| `city` | `CharField` | Город |
| `avatar` | `ImageField` | Аватар |
| `is_active` | `BooleanField` | Активен |
| `is_staff` | `BooleanField` | Доступ в админку |
| `is_superuser` | `BooleanField` | Суперпользователь |

### 📚 Course (Курс)

| Поле | Тип | Описание |
|:-----|:----|:---------|
| `title` | `CharField` | Название |
| `preview` | `ImageField` | Превью |
| `description` | `TextField` | Описание |
| `price` | `DecimalField` | Цена, руб. (в Stripe уходит в копейках) |
| `updated_at` | `DateTimeField` | Автообновление при `save()` (для кулдауна 4 ч) |
| `owner` | `ForeignKey` | Владелец |

### 📖 Lesson (Урок)

| Поле | Тип | Описание |
|:-----|:----|:---------|
| `title` | `CharField` | Название |
| `description` | `TextField` | Описание |
| `preview` | `ImageField` | Превью |
| `video_link` | `URLField` | Ссылка на видео |
| `course` | `ForeignKey` | Курс (`related_name='lessons'`) |
| `owner` | `ForeignKey` | Владелец |

### 🔔 Subscription (Подписка)

| Поле | Тип | Описание |
|:-----|:----|:---------|
| `user` | `ForeignKey` | Подписчик |
| `course` | `ForeignKey` | Курс |
| `created_at` | `DateTimeField` | Дата подписки |

### 💳 Payment (Платёж)

| Поле | Тип | Описание |
|:-----|:----|:---------|
| `user` | `ForeignKey` | Пользователь |
| `payment_date` | `DateTimeField` | Дата оплаты |
| `course` | `ForeignKey` | Оплаченный курс |
| `lesson` | `ForeignKey` | Оплаченный урок |
| `amount` | `PositiveIntegerField` | Сумма **в копейках** |
| `payment_method` | `CharField` | `cash` / `transfer` |
| `status` | `CharField` | `unpaid` / `paid` |
| `stripe_product_id` | `CharField` | ID продукта Stripe |
| `stripe_price_id` | `CharField` | ID цены Stripe |
| `stripe_session_id` | `CharField` | ID Checkout Session (`unique`, `db_index`) |
| `payment_url` | `URLField` | Ссылка на оплату |

---

## 🔐 Роли и права доступа

### 👤 Пользователь

| Действие | Доступ |
|:---------|:------:|
| Просмотр, редактирование, удаление **своих** курсов и уроков | ✅ |
| Создание курсов и уроков | ✅ |
| Просмотр чужих курсов и уроков | ❌ |
| Просмотр чужих платежей | ❌ |
| Просмотр своего профиля и платежей | ✅ |

### 🛡️ Модератор (группа «Модераторы»)

| Действие | Доступ |
|:---------|:------:|
| Просмотр **всех** курсов и уроков | ✅ |
| Редактирование **любых** курсов и уроков | ✅ |
| Создание курсов и уроков | ❌ |
| Удаление курсов и уроков | ❌ |

> Роли назначаются через админку. Группа создаётся фикстурой `users/fixtures/groups.json`.

---

## ⚡ Дополнительные возможности

| Возможность | Где | Описание |
|:------------|:----|:---------|
| `lessons_count` | `CourseSerializer` | Количество уроков через `SerializerMethodField` |
| Вложенные уроки | `CourseSerializer` | `lessons = LessonSerializer(many=True)` |
| История платежей | `UserProfileSerializer` | `payments = PaymentSerializer(many=True)` |
| JWT | `settings.py` | `JWTAuthentication`, lifetime 60 мин |
| Фильтрация | `PaymentFilter` | ordering, course, lesson, payment_method |
| Swagger / ReDoc | `settings.py` | drf-spectacular, `/api/docs/`, `/api/redoc/` |
| Stripe Checkout | `lms/services.py` | product → price (копейки) → session |
| Рассылка при обновлении курса | `lms/tasks.py` | `send_course_update_email` |
| Кулдаун 4 часа | `lms/views.py` | `timezone.now() - previous_updated_at < timedelta(hours=4)` |
| Блокировка неактивных | `users/tasks.py` | `last_login < now - 30 дней` → `is_active=False` (батч) |


## ⚙️ Celery, Redis и фоновые задачи

### Что реализовано

| Задача | Где | Описание |
|:-------|:----|:---------|
| `send_course_update_email` | `lms/tasks.py` | Письмо подписчикам при обновлении курса или урока. Вызов из контроллера **после** `save()`. Кулдаун: не чаще раза в 4 часа. |
| `deactivate_inactive_users` | `users/tasks.py` | Блокировка пользователей, не заходивших > 30 дней. Батч через `QuerySet.update()` — один SQL-запрос. |
| `beat_schedule` | `drf_school/celery.py` | `deactivate-inactive-users` ежедневно в 03:00 (`crontab(hour=3, minute=0)`). |

### Переменные окружения (`.env`)

| Переменная | Пример | Назначение |
|:-----------|:-------|:-----------|
| `REDIS_URL` | `redis://localhost:6379/0` | Общий URL Redis |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Брокер |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Result backend |
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` | Для разработки — письма в консоль |
| `DEFAULT_FROM_EMAIL` | `noreply@drf-school.local` | Отправитель |

### Таймзона

`CELERY_TIMEZONE` в `settings.py` **равен** `TIME_ZONE` — задачи beat запускаются в 03:00 по локальному времени проекта.

```python
TIME_ZONE = "Europe/Moscow"
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False
```
### Запуск Redis

Redis не имеет официальной сборки для Windows. Варианты:

| Способ | Команда / действие |
|:-------|:-------------------|
| WSL2 (рекомендуется) | `wsl --install` → `sudo apt-get install redis-server` → `sudo service redis-server start` |
| Memurai | Нативный Redis-совместимый сервер для Windows |
| Docker | `docker run -d -p 6379:6379 redis` |

Проверка: `redis-cli ping` → `PONG`.

### Запуск Celery

| Терминал | Команда |
|:---------|:--------|
| Worker (Windows — обязательно `--pool=solo`) | `celery -A drf_school worker -l info --pool=solo` |
| Beat (расписание) | `celery -A drf_school beat -l info` |
| Django | `python manage.py runserver` |

> ⚠️ На Windows пул `prefork` не работает — используйте `--pool=solo` или `-P eventlet` (`pip install eventlet`).

### Как проверить

**Рассылка при обновлении курса:**

```http
PATCH /courses/1/
Authorization: Bearer <access>

{ "title": "Новое название" }
```

В консоли worker'а появится письмо. Повторный `PATCH` в течение 4 часов — письма **не будет** (кулдаун).

**Блокировка неактивных:**

```powershell
python manage.py shell
>>> from users.tasks import deactivate_inactive_users
>>> deactivate_inactive_users.delay()
# в логах worker: Task users.tasks.deactivate_inactive_users succeeded
```

Проверка результата:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(is_active=False).count()
```

---


---

## 🚀 Запуск проекта

### 1. Клонирование

```bash
git clone https://github.com/your-username/drf_school.git
cd drf_school
```
2. Виртуальное окружение
````
Windows:

powershell
python -m venv .venv
.venv\Scripts\activate
Linux/macOS:


python3 -m venv .venv
source .venv/bin/activate
````
3. Зависимости
````
powershell
pip install -r requirements.txt
````
4. .env
````
Создайте .env на основе .env.example:
````
5. Миграции

```powershell
python manage.py makemigrations
python manage.py migrate
````
6. Группа «Модераторы»
```powershell
python manage.py loaddata users/fixtures/groups.json
```
7. Платежи
```powershell
python manage.py load_payments
```
8. Суперпользователь
```powershell
python manage.py createsuperuser
```
9. Redis + Celery
```powershell
# Redis (WSL/Memurai/Docker) — см. раздел "Celery, Redis"
redis-cli ping

# Worker (Windows — --pool=solo)
celery -A drf_school worker -l info --pool=solo

# Beat (в отдельном терминале)
celery -A drf_school beat -l info
```
10. Запуск
```powershell
python manage.py runserver
Сервер: http://127.0.0.1:8000/
```

## 🔒 Безопасность репозитория

В репозитории **не хранятся**:

| Файл | Причина |
|:-----|:--------|
| `.env` | Содержит `SECRET_KEY` |
| `db.sqlite3` | Локальная база с данными |
| `media/` | Загруженные пользователями файлы |
| `.venv/` | Виртуальное окружение |

В репозитории **есть** только `.env.example` с примерами переменных без реальных значений.
## 🧪 Проверка в Postman

Получить токен
```http
POST http://127.0.0.1:8000/token/
Content-Type: application/json

{
  "email": "admin@school.ru",
  "password": "admin12345"
}
```
### Ответ:
````
json
{
  "refresh": "...",
  "access": "..."
}
````
### Использовать токен
```http
GET http://127.0.0.1:8000/courses/
Authorization: Bearer <access>
```
## 🧪 Сценарии проверки в Postman

| №  | Сценарий                                    | Ожидание                               |
|:--:|:--------------------------------------------|:---------------------------------------|
| 1  | `POST /register/`                           | ✅ 201 Created                         |
| 2  | `POST /token/`                              | ✅ `access` + `refresh`                |
| 3  | `GET /courses/` без токена                  | ❌ 401 Unauthorized                    |
| 4  | `GET /courses/` с токеном                   | ✅ свои / все (модератор)              |
| 5  | `POST /courses/` модератором                | ❌ 403 Forbidden                       |
| 6  | `DELETE /courses/1/` модератором            | ❌ 403 Forbidden                       |
| 7  | `GET /payments/?ordering=-payment_date`     | ✅ убывание                            |
| 8  | `GET /payments/?course=1`                   | ✅ фильтр по курсу                     |
| 9  | `GET /payments/?payment_method=cash`        | ✅ фильтр по способу                   |
| 10 | `GET /users/profile/`                       | ✅ профиль + платежи                   |
| 11 | `POST /subscriptions/` `{"course_id": 1}`   | ✅ 201 (добавлена) / 200 (удалена)     |
| 12 | `POST /payments/create/` `{"course_id": 1}` | ✅ 201 + `payment_url`, `session_id`   |
| 13 | `GET /payments/status/<session_id>/`        | ✅ `payment_status: "paid"`            |
| 14 | `PATCH /courses/1/` (обновление)            | ✅ в логах worker — письмо подписчикам |
| 15 | `PATCH /courses/1/` повторно < 4 ч          | ✅ письма нет (кулдаун)                |
| 16 | Запуск `deactivate_inactive_users`          | ✅ неактивные: `is_active=False`       |
| 17 | `GET /api/docs/`                            | ✅ Swagger UI открывается              |

---

## 🔧 Команды для разработки

| Команда                                          | Описание                    |
|:-------------------------------------------------|:----------------------------|
| `python manage.py runserver`                     | 🚀 Запуск сервера           |
| `python manage.py makemigrations`                | 📦 Создание миграций        |
| `python manage.py migrate`                       | 🗄️ Применение миграций      |
| `python manage.py createsuperuser`               | 👑 Создание администратора  |
| `python manage.py shell`                         | 💻 Интерактивная оболочка   |
| `python manage.py loaddata <fixture>`            | 📥 Загрузка фикстур         |
| `python manage.py load_payments`                 | 💳 Загрузка платежей        |
| `python manage.py test`                          | 🧪 Запуск тестов            |
| `python manage.py spectacular --file schema.yml` | 📘 Генерация OpenAPI-схемы  |
| `celery -A drf_school worker -l info --pool=solo`| ⚙️ Celery worker (Windows)  |
| `celery -A drf_school beat -l info`              | ⏰ Celery beat (расписание) |
| `redis-cli ping`                                 | 🔴 Проверка Redis (`PONG`)  |
| `pip freeze > requirements.txt`                  | 📋 Обновление зависимостей  |

## 📝 Лицензия
Учебный проект. Не для коммерческого использования.

## 👤 Автор
### 1. Имя: Геннадий Кокаулин
### 2. Email: Genchik691@gmail.com
### 3. GitHub: https://github.com/genchik691