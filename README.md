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
| Pillow | 11.0+ | Работа с изображениями |
| SQLite | 3 | База данных (разработка) |

---

## 📂 Структура проекта
````
drf_school/
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── db.sqlite3
│
├── drf_school/ # Настройки проекта
│ ├── init.py
│ ├── settings.py # JWT, DRF, AUTH_USER_MODEL
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
│ ├── views.py # Register, UserViewSet, Profile, Payments
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
│ ├── models.py # Course, Lesson
│ ├── serializers.py # Course, Lesson
│ ├── views.py # CourseViewSet, Lesson Generic
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

### 💳 Платежи

| Метод | URL | Доступ |
|:------|:----|:------:|
| `GET` | `/payments/` | 🔒 (только свои) |

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

### 💳 Payment (Платёж)

| Поле | Тип | Описание |
|:-----|:----|:---------|
| `user` | `ForeignKey` | Пользователь |
| `payment_date` | `DateTimeField` | Дата оплаты |
| `course` | `ForeignKey` | Оплаченный курс |
| `lesson` | `ForeignKey` | Оплаченный урок |
| `amount` | `DecimalField` | Сумма |
| `payment_method` | `CharField` | `cash` / `transfer` |

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
9. Запуск
```powershell
python manage.py runserver
Сервер: http://127.0.0.1:8000/
```

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

| № | Сценарий | Ожидание |
|:-:|:---------|:---------|
| 1 | `POST /register/` | ✅ 201 Created |
| 2 | `POST /token/` | ✅ `access` + `refresh` |
| 3 | `GET /courses/` без токена | ❌ 401 Unauthorized |
| 4 | `GET /courses/` с токеном | ✅ свои / все (модератор) |
| 5 | `POST /courses/` модератором | ❌ 403 Forbidden |
| 6 | `DELETE /courses/1/` модератором | ❌ 403 Forbidden |
| 7 | `GET /payments/?ordering=-payment_date` | ✅ убывание |
| 8 | `GET /payments/?course=1` | ✅ фильтр по курсу |
| 9 | `GET /payments/?payment_method=cash` | ✅ фильтр по способу |
| 10 | `GET /users/profile/` | ✅ профиль + платежи |

---

## 🔧 Команды для разработки

| Команда | Описание |
|:--------|:---------|
| `python manage.py runserver` | 🚀 Запуск сервера |
| `python manage.py makemigrations` | 📦 Создание миграций |
| `python manage.py migrate` | 🗄️ Применение миграций |
| `python manage.py createsuperuser` | 👑 Создание администратора |
| `python manage.py shell` | 💻 Интерактивная оболочка |
| `python manage.py loaddata <fixture>` | 📥 Загрузка фикстур |
| `python manage.py load_payments` | 💳 Загрузка платежей |
| `python manage.py test` | 🧪 Запуск тестов |
| `pip freeze > requirements.txt` | 📋 Обновление зависимостей |

## 📝 Лицензия
Учебный проект. Не для коммерческого использования.

## 👤 Автор
### 1. Имя: Геннадий Кокаулин
### 2. Email: Genchik691@gmail.com
### 3. GitHub: https://github.com/genchik691