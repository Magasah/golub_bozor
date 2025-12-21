# 🚀 DJANGO КОМАНДЫ - Шпаргалка

## 📦 Управление проектом

### Запуск сервера разработки
```bash
python manage.py runserver
python manage.py runserver 8080          # На другом порту
python manage.py runserver 0.0.0.0:8000  # Доступ из сети
```

### Создание приложения
```bash
python manage.py startapp app_name
```

---

## 🗄️ База данных

### Миграции
```bash
# Создать миграции
python manage.py makemigrations

# Создать для конкретного приложения
python manage.py makemigrations core

# Применить миграции
python manage.py migrate

# Откатить миграцию
python manage.py migrate core 0001

# Показать SQL миграции
python manage.py sqlmigrate core 0001

# Проверить проблемы с миграциями
python manage.py showmigrations
```

### Очистка БД
```bash
# Удалить все данные
python manage.py flush

# Сбросить БД (удалить db.sqlite3и создать заново)
# Windows
del db.sqlite3
python manage.py migrate

# Linux/Mac
rm db.sqlite3
python manage.py migrate
```

---

## 👤 Пользователи

### Создать суперпользователя
```bash
python manage.py createsuperuser
```

### Создать пользователя через shell
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('username', 'email@test.com', 'password123')
```

### Сменить пароль
```bash
python manage.py changepassword username
```

---

## 🐚 Django Shell

### Запуск shell
```bash
python manage.py shell

# С IPython (если установлен)
python manage.py shell -i ipython
```

### Полезные команды в shell
```python
# Импорт моделей
from core.models import Pigeon
from django.contrib.auth.models import User

# Просмотр всех объектов
Pigeon.objects.all()

# Количество
Pigeon.objects.count()

# Создать объект
p = Pigeon.objects.create(title="Test", price=1000, ...)

# Выход
exit()
```

---

## 📊 Данные (Fixtures)

### Экспорт данных
```bash
# Все приложение
python manage.py dumpdata core > core_data.json

# Конкретная модель
python manage.py dumpdata core.Pigeon > pigeons.json

# С форматированием
python manage.py dumpdata core.Pigeon --indent 2 > pigeons.json

# Без первичных ключей (для переноса между БД)
python manage.py dumpdata core.Pigeon --natural-foreign --natural-primary > pigeons.json
```

### Импорт данных
```bash
python manage.py loaddata pigeons.json
python manage.py loaddata core_data.json
```

---

## 🧹 Очистка и обслуживание

### Удалить миграции (сбросить)
```bash
# Windows
del /Q core\migrations\0*.py

# Linux/Mac
rm core/migrations/0*.py

# Затем создать заново
python manage.py makemigrations
python manage.py migrate
```

### Очистить кэш (если используется)
```bash
python manage.py clear_cache
```

---

## 🔍 Проверка и тестирование

### Проверка проекта на ошибки
```bash
python manage.py check
python manage.py check --deploy  # Проверка для продакшена
```

### Запуск тестов
```bash
# Все тесты
python manage.py test

# Конкретное приложение
python manage.py test core

# С подробным выводом
python manage.py test --verbosity=2
```

### SQL запросы (дебаг)
```bash
python manage.py dbshell  # Открыть SQL консоль
```

---

## 📁 Статические файлы

### Собрать статику (для продакшена)
```bash
python manage.py collectstatic

# Без подтверждения
python manage.py collectstatic --noinput
```

---

## 🔐 Безопасность

### Сгенерировать новый SECRET_KEY
```bash
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

---

## 🌐 Интернационализация

### Создать файлы переводов
```bash
python manage.py makemessages -l ru
python manage.py makemessages -l en

# Компилировать переводы
python manage.py compilemessages
```

---

## 📝 Кастомные команды (если созданы)

### Создать кастомную команду
Создайте файл: `core/management/commands/mycommand.py`

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Описание команды'
    
    def handle(self, *args, **options):
        self.stdout.write('Hello World!')
```

### Запуск
```bash
python manage.py mycommand
```

---

## 🛠️ Полезные комбинации

### Полный сброс и настройка проекта
```bash
# Windows
del db.sqlite3
del /Q core\migrations\0*.py
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Linux/Mac
rm db.sqlite3
rm core/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Быстрое тестирование
```bash
python manage.py makemigrations && python manage.py migrate && python manage.py runserver
```

---

## 📋 Информационные команды

### Версия Django
```bash
python manage.py version
python -m django --version
```

### Список всех команд
```bash
python manage.py help
python manage.py help <command>  # Помощь по конкретной команде
```

### Настройки проекта
```bash
python manage.py diffsettings  # Показать измененные настройки
```

### SQL схема
```bash
python manage.py inspectdb  # Сгенерировать модели из существующей БД
```

---

## 🎯 Специфичные для GolubBozor

### Создать тестового пользователя с голубями
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from core.models import Pigeon
>>> user = User.objects.create_user('test', 'test@example.com', 'test123')
>>> Pigeon.objects.create(
...     title='Тестовый голубь',
...     price=1000,
...     description='Описание',
...     phone='+992 900 000 000',
...     owner=user
... )
```

### Посмотреть все VIP объявления
```bash
python manage.py shell
>>> from core.models import Pigeon
>>> vip = Pigeon.objects.filter(is_vip=True)
>>> for p in vip:
...     print(f"{p.title}: {p.price} TJS")
```

---

## 🐛 Отладка

### Показать SQL запросы
```python
# В shell
from django.db import connection
Pigeon.objects.all()
print(connection.queries)
```

### Включить отладку SQL (settings.py)
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## 💡 Pro Tips

1. **Виртуальное окружение:** Всегда активируйте venv перед запуском команд
2. **Миграции:** Делайте `makemigrations` после каждого изменения models.py
3. **Бэкап:** Экспортируйте данные перед большими изменениями
4. **Shell:** Используйте shell для быстрого тестирования запросов
5. **Логи:** Проверяйте консоль на ошибки при запуске сервера

---

**🚀 Готово! Теперь вы знаете все основные команды Django для работы с GolubBozor!**
