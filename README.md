# DRF Home Works - Образовательная платформа

Django REST Framework проект для управления образовательными курсами и уроками с системой подписок, платежей и уведомлений.

## 🛠 Технологии

- **Backend**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL 15
- **Cache & Message Broker**: Redis
- **Task Queue**: Celery + Celery Beat
- **Authentication**: JWT + Session
- **Payments**: Stripe Integration
- **Containerization**: Docker + Docker Compose

## 📦 Запуск проекта

### Требования
- Docker
- Docker Compose

### Быстрый старт

1. **Клонируйте репозиторий**:
```bash
git clone <repository-url>
cd drf_home_works
```
2. **Настройте переменные окружения**:
Создайте файл .env на основе .env.template:

Заполните необходимые переменные (особенно для базы данных, email и Stripe).

3. **Запустите проект**:

bash
docker compose up --build

4. Проект будет доступен по адресу: http://localhost:8000

5. **Создайте суперпользователя**:
```bash
docker compose exec web python manage.py create_superuser
```
Или классическим способом:
```bash
docker compose exec web python manage.py createsuperuser
```

6. **Заполните базу данных тестовыми данными**:

```bash
# Загрузить курсы и уроки
docker compose exec web python manage.py load_lms_data

# Создать тестовые платежи
docker compose exec web python manage.py load_payments

# Создать модератора
docker compose exec web python manage.py create_moderator
```
