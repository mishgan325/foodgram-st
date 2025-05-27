# Foodgram

## Описание проекта

**Foodgram** — это веб-приложение для публикации рецептов, добавления их в избранное и формирования списка покупок. Пользователи могут делиться рецептами, подписываться на других авторов и планировать своё меню.

## Технологии

- Python 3.10
- Django / Django REST Framework
- PostgreSQL
- Docker / Docker Compose
- Gunicorn
- (Frontend: React — если используется)
- Postman / Newman (для тестирования API)
- reportlab

## Установка и запуск проекта

### 1. Запуск с помощью Docker

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/mishgan325/foodgram-st
   cd foodgram-st
   ```

2. Создайте файл `.env` в папке infra и заполните переменные окружения (пример в `.env.example`).

3. Соберите и запустите контейнеры:
   ```
   docker-compose up --build
   ```

4. Приложение будет доступно по адресу:  
   - http://localhost/ — фронтенд  
   - http://localhost/api/ — API  
   - http://localhost/api/docs/ — документация API
   - http://localhost/admin/ - админ зона Django

   admin@admin.admin admin123 - почта и пароль администратора

### 2. Локальный запуск без Docker

1. Установите Python 3.10 и PostgreSQL.
2. Клонируйте репозиторий и перейдите в папку backend:
   ```
   git clone https://github.com/mishgan325/foodgram-st
   cd foodgram-st/backend
   ```
3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
4. Настройте переменные окружения (создайте `.env`).
5. Выполните миграции и соберите статику:
   ```
   python manage.py migrate
   python manage.py collectstatic
   ```
6. Запустите сервер:
   ```
   python manage.py runserver
   ```

## Автор
Шибут Михаил, ИКБО-02-22
- [Почта для связи](shibut.michael@yandex.ru)