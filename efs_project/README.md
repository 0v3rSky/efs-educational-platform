# EFS Project

## Установка проекта

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd efs_project
```

2. Создайте виртуальное окружение и активируйте его:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env в корневой директории проекта и добавьте необходимые переменные окружения:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер разработки:
```bash
python manage.py runserver
```

## Структура проекта

- `accounts/` - приложение для аутентификации и регистрации
- `courses/` - приложение для курсов
- `main/` - главное приложение
- `quests/` - приложение для квестов
- `tests/` - приложение для тестов
- `users/` - приложение для пользователей
- `media/` - директория для загруженных файлов
- `efs_project/` - основные настройки проекта

## Важные замечания

1. Убедитесь, что у вас установлен Python 3.8 или выше
2. Для работы с изображениями требуется Pillow
3. Для отправки email требуется настроить SMTP-сервер
4. В production необходимо изменить DEBUG=False и использовать безопасный SECRET_KEY 