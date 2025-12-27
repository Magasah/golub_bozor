# 🚀 ИНСТРУКЦИЯ ПО ДЕПЛОЮ GOLUB BOZOR
## От разработки до продакшена на PythonAnywhere

---

## 📋 СОДЕРЖАНИЕ
1. [Очистка проекта](#1-очистка-проекта)
2. [Подготовка к Git](#2-подготовка-к-git)
3. [Настройка безопасности](#3-настройка-безопасности)
4. [Загрузка на GitHub](#4-загрузка-на-github)
5. [Деплой на PythonAnywhere](#5-деплой-на-pythonanywhere)
6. [Чек-лист перед запуском](#6-чек-лист-перед-запуском)

---

## 1. ОЧИСТКА ПРОЕКТА

### Что НУЖНО удалить перед Git:

```bash
# Запустите в корне проекта (PowerShell):

# 1. Удалить кеш Python
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# 2. Удалить тестовые скрипты
Remove-Item -Path "test_*.py", "debug_*.py", "check_*.py" -ErrorAction SilentlyContinue

# 3. Удалить специфичные скрипты
Remove-Item -Path "create_health_articles.py", "add_images_to_articles.py", "security_audit.py" -ErrorAction SilentlyContinue

# 4. Очистить media (ОСТОРОЖНО! Сохраните нужные файлы!)
# Remove-Item -Path "media/*" -Recurse -Force -ErrorAction SilentlyContinue
# (Оставьте .gitkeep файл)

# 5. Удалить локальную БД (если не нужна)
# Remove-Item -Path "db.sqlite3" -ErrorAction SilentlyContinue

# 6. Удалить IDE настройки
Remove-Item -Path ".vscode" -Recurse -Force -ErrorAction SilentlyContinue
```

### Автоматическая очистка (один скрипт):

Создайте файл `cleanup.ps1`:

```powershell
Write-Host "🧹 Очистка проекта GolubBozor..." -ForegroundColor Cyan

# Удаляем __pycache__
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Write-Host "✅ Удалён __pycache__" -ForegroundColor Green

# Удаляем .pyc файлы
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
Write-Host "✅ Удалены .pyc файлы" -ForegroundColor Green

# Удаляем тестовые скрипты
$testFiles = @(
    "test_*.py",
    "debug_*.py", 
    "check_*.py",
    "create_health_articles.py",
    "add_images_to_articles.py",
    "security_audit.py"
)

foreach ($pattern in $testFiles) {
    Get-ChildItem -Path . -Filter $pattern | Remove-Item -Force -ErrorAction SilentlyContinue
}
Write-Host "✅ Удалены тестовые скрипты" -ForegroundColor Green

# Удаляем .vscode
if (Test-Path ".vscode") {
    Remove-Item -Path ".vscode" -Recurse -Force
    Write-Host "✅ Удалён .vscode" -ForegroundColor Green
}

Write-Host "`n🎉 Проект очищен и готов к Git!" -ForegroundColor Green
```

Запуск: `.\cleanup.ps1`

---

## 2. ПОДГОТОВКА К GIT

### Шаг 1: Проверьте .gitignore

Файл `.gitignore` уже создан. Проверьте что он на месте:
```bash
ls .gitignore
```

### Шаг 2: Создайте .env файл

**ВАЖНО:** Файл `.env` НЕ должен попасть в Git!

```bash
# Скопируйте пример:
Copy-Item .env.example .env

# Отредактируйте .env и заполните реальные значения
notepad .env
```

**Обязательно измените:**
- `SECRET_KEY` - сгенерируйте новый ключ
- `DEBUG` - поставьте False для продакшена
- Telegram токены (если используются)

### Шаг 3: Сгенерируйте новый SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Скопируйте результат в `.env` файл.

---

## 3. НАСТРОЙКА БЕЗОПАСНОСТИ

### ✅ Уже настроено в проекте:

- ✅ SECRET_KEY через переменные окружения
- ✅ DEBUG читается из .env
- ✅ ALLOWED_HOSTS настроен
- ✅ Security headers включены
- ✅ CSRF protection активна
- ✅ Session security настроена
- ✅ Password validators активны
- ✅ Django Axes для защиты от брутфорса

### ⚠️ Что нужно сделать вручную:

1. **Для продакшена создайте новый .env:**

```bash
# На сервере PythonAnywhere создайте файл .env:
nano .env

# И заполните:
SECRET_KEY=<ваш-новый-секретный-ключ>
DEBUG=False
ALLOWED_HOSTS=magaj.pythonanywhere.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SITE_DOMAIN=https://magaj.pythonanywhere.com
```

2. **Проверьте безопасность:**

```bash
# Локально запустите проверку:
python security_audit.py

# Должно быть минимум 90% успешных проверок
```

---

## 4. ЗАГРУЗКА НА GITHUB

### Шаг 1: Инициализация Git

```bash
# Если ещё не инициализирован:
git init

# Добавьте все файлы:
git add .

# Проверьте что НЕ добавилось лишнего:
git status

# Должны быть проигнорированы:
# - .env
# - venv/
# - __pycache__/
# - media/ (кроме .gitkeep)
# - db.sqlite3
```

### Шаг 2: Первый коммит

```bash
git commit -m "Initial commit: GolubBozor v1.0 - Premium Pigeon Marketplace

Features:
- User authentication and profiles
- Pigeon listings (fixed price & auctions)
- Bidding system
- VIP placements
- Health encyclopedia (bilingual RU/TJ)
- Manager dashboard
- Telegram notifications
- PWA support
- Security hardened"
```

### Шаг 3: Создайте репозиторий на GitHub

1. Зайдите на https://github.com/new
2. Название: `golub-bozor` или `pigeon-marketplace`
3. Описание: `Premium Pigeon Marketplace - Django web application for buying/selling pigeons in Tajikistan`
4. **Приватный или публичный** - на ваш выбор
5. НЕ добавляйте README, .gitignore, license (у нас уже есть)

### Шаг 4: Загрузите код

```bash
# Добавьте remote (замените YOUR_USERNAME):
git remote add origin https://github.com/YOUR_USERNAME/golub-bozor.git

# Отправьте код:
git branch -M main
git push -u origin main
```

---

## 5. ДЕПЛОЙ НА PYTHONANYWHERE

### Шаг 1: Регистрация и настройка

1. Зарегистрируйтесь на https://www.pythonanywhere.com
2. Выберите тариф (Beginner для начала)
3. Ваш домен: `magaj.pythonanywhere.com`

### Шаг 2: Клонирование проекта

В PythonAnywhere Bash консоли:

```bash
# Клонируйте репозиторий:
git clone https://github.com/YOUR_USERNAME/golub-bozor.git
cd golub-bozor

# Создайте виртуальное окружение:
mkvirtualenv --python=/usr/bin/python3.11 golub-env

# Активируйте (если не активировано):
workon golub-env

# Установите зависимости:
pip install -r requirements.txt
```

### Шаг 3: Настройка переменных окружения

```bash
# Создайте .env файл:
nano .env

# Заполните (НЕ копируйте локальный .env!):
SECRET_KEY=<новый-секретный-ключ-для-продакшена>
DEBUG=False
ALLOWED_HOSTS=magaj.pythonanywhere.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SITE_DOMAIN=https://magaj.pythonanywhere.com
TELEGRAM_BOT_TOKEN=<ваш-токен>
TELEGRAM_CHAT_ID=<ваш-chat-id>

# Сохраните: Ctrl+O, Enter, Ctrl+X
```

### Шаг 4: Миграции и статика

```bash
# Миграции базы данных:
python manage.py migrate

# Создайте суперпользователя:
python manage.py createsuperuser

# Соберите статические файлы:
python manage.py collectstatic --noinput
```

### Шаг 5: Настройка Web App

1. Зайдите в **Web** раздел PythonAnywhere
2. Нажмите **Add a new web app**
3. Выберите **Manual configuration**
4. Python version: **3.11**

**Настройки:**

**Source code:**
```
/home/magaj/golub-bozor
```

**Virtualenv:**
```
/home/magaj/.virtualenvs/golub-env
```

**WSGI configuration file:**
Нажмите на ссылку и замените содержимое:

```python
import os
import sys

# Путь к проекту
path = '/home/magaj/golub-bozor'
if path not in sys.path:
    sys.path.insert(0, path)

# Переменные окружения
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Загрузка .env
from dotenv import load_dotenv
project_folder = os.path.expanduser(path)
load_dotenv(os.path.join(project_folder, '.env'))

# Django WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Static files:**
- URL: `/static/`
- Directory: `/home/magaj/golub-bozor/staticfiles`

**Media files:**
- URL: `/media/`
- Directory: `/home/magaj/golub-bozor/media`

### Шаг 6: Перезагрузка

Нажмите зелёную кнопку **Reload** вверху страницы.

Откройте https://magaj.pythonanywhere.com

---

## 6. ЧЕК-ЛИСТ ПЕРЕД ЗАПУСКОМ

### 🔒 Безопасность:

- [ ] ✅ SECRET_KEY уникальный для продакшена
- [ ] ✅ DEBUG = False
- [ ] ✅ ALLOWED_HOSTS содержит только ваш домен
- [ ] ✅ .env не в Git
- [ ] ✅ HTTPS настроен (SECURE_SSL_REDIRECT=True)
- [ ] ✅ Все пароли сильные и уникальные

### 📁 Файлы:

- [ ] ✅ .gitignore на месте
- [ ] ✅ requirements.txt актуален
- [ ] ✅ README.md описывает проект
- [ ] ✅ media/ пустая (или с .gitkeep)
- [ ] ✅ Нет __pycache__ в Git

### 🌐 Деплой:

- [ ] ✅ Миграции применены
- [ ] ✅ Статика собрана
- [ ] ✅ Суперпользователь создан
- [ ] ✅ WSGI настроен
- [ ] ✅ Static/Media пути прописаны
- [ ] ✅ Сайт открывается без ошибок

### 🧪 Тестирование:

- [ ] ✅ Регистрация работает
- [ ] ✅ Вход/выход работает
- [ ] ✅ Создание объявления работает
- [ ] ✅ Загрузка фото работает
- [ ] ✅ Админка доступна
- [ ] ✅ Страница энциклопедии открывается

---

## 📞 ПОДДЕРЖКА

**Ошибки на PythonAnywhere:**
1. Проверьте логи: **Web → Log files → Error log**
2. Проверьте .env файл: `cat .env`
3. Проверьте права доступа: `ls -la`

**Статика не загружается:**
```bash
python manage.py collectstatic --noinput
```

**База данных пустая:**
```bash
python manage.py migrate
python manage.py createsuperuser
```

**Перезагрузить сервер:**
- Нажмите зелёную кнопку **Reload** в Web разделе

---

## 🎉 ГОТОВО!

Ваш сайт должен работать по адресу:
**https://magaj.pythonanywhere.com**

Админка:
**https://magaj.pythonanywhere.com/admin**

---

**Удачи! 🚀**
