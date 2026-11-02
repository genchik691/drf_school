# drf_school — DRF-проект

Django + DRF: школа с курсами и уроками, кастомный пользователь с авторизацией по email.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
## 🌐 Эндпоинты

| Метод | URL | Назначение |
|:------|:----|:-----------|
| `GET` | `/courses/` | Список курсов |
| `POST` | `/courses/` | Создать курс |
| `GET` | `/courses/<id>/` | Один курс |
| `PUT/PATCH` | `/courses/<id>/` | Изменить курс |
| `DELETE` | `/courses/<id>/` | Удалить курс |
| `GET` | `/lessons/` | Список уроков |
| `POST` | `/lessons/` | Создать урок |
| `GET` | `/lessons/<id>/` | Один урок |
| `PUT/PATCH` | `/lessons/<id>/` | Изменить урок |
| `DELETE` | `/lessons/<id>/` | Удалить урок |
| `GET` | `/users/<id>/` | Профиль |
| `PATCH` | `/users/<id>/` | Редактировать профиль |
## Модели
### User — email (USERNAME_FIELD), phone, city, avatar

### Course — title, preview, description

### Lesson — title, description, preview, video_link, course (FK)



---

## 🚀 ЗАПУСК


## 1. Миграции
````
python manage.py makemigrations
python manage.py migrate
````
## 2. Суперпользователь
````
python manage.py createsuperuser
````
### Email: admin@school.ru
### Password: admin12345

## 3. Проверка
````
python manage.py check
````

## 4. Запуск
````
python manage.py runserver
````
## ✅ Проверка в Postman

| Метод | URL | Тело запроса |
|:------|:----|:-------------|
| `POST` | `http://127.0.0.1:8000/courses/` | `{"title": "Django", "description": "Курс"}` |
| `GET` | `http://127.0.0.1:8000/courses/` | — |
| `POST` | `http://127.0.0.1:8000/lessons/` | `{"title": "Урок 1", "course": 1}` |
| `GET` | `http://127.0.0.1:8000/lessons/1/` | — |
| `PATCH` | `http://127.0.0.1:8000/users/1/` | `{"phone": "+7999..."}` |