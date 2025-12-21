# 🚀 БЫСТРЫЙ СТАРТ - ДЕПЛОЙ НА RENDER.COM

## Что нужно:
- ✅ Email
- ✅ GitHub аккаунт
- ⏱️ Время: 30 минут

## Пошаговая инструкция:

### 1️⃣ ЗАГРУЗИ НА GITHUB (10 мин)

```powershell
cd C:\Users\spart\Documents\Project\golub_bozor
git init
git add .
git commit -m "Initial commit"
```

Создай репозиторий на https://github.com/new
Имя: `golub_bozor`

```powershell
git remote add origin https://github.com/твой-username/golub_bozor.git
git branch -M main
git push -u origin main
```

### 2️⃣ ЗАРЕГИСТРИРУЙСЯ НА RENDER (2 мин)

- Открой: https://render.com
- **"Get Started for Free"**
- **"Sign up with GitHub"**
- Подтверди email

### 3️⃣ СОЗДАЙ WEB SERVICE (5 мин)

1. **"New +"** → **"Web Service"**
2. **"Connect a repository"** → выбери `golub_bozor`
3. Настрой:
   - Name: `golub-bozor`
   - Runtime: `Python 3`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn config.wsgi:application`
   - Instance Type: **Free**

4. Environment Variables:
   - `PYTHON_VERSION` = `3.11.7`
   - `DEBUG` = `False`
   - `SECRET_KEY` = `gjdk49fj2kf9dkf0d9kf0dk3f9dkf0d9kf0d9kf0d9kf0dk`

5. **"Create Web Service"**

### 4️⃣ СОЗДАЙ БАЗУ ДАННЫХ (3 мин)

1. **"New +"** → **"PostgreSQL"**
2. Настрой:
   - Name: `golub-bozor-db`
   - Database: `golub_bozor`
   - Instance Type: **Free**
3. **"Create Database"**

### 5️⃣ ПОДКЛЮЧИ БД (2 мин)

1. Открой Web Service
2. Вкладка **"Environment"**
3. Найди `DATABASE_URL`
4. **"Add from Database"** → выбери `golub-bozor-db`
5. **"Save Changes"**

### 6️⃣ СОЗДАЙ АДМИНА (3 мин)

1. Вкладка **"Shell"**
2. **"Launch Shell"**
3. Выполни:
   ```bash
   python manage.py createsuperuser
   ```
4. Введи username, password

### 7️⃣ ГОТОВО! 🎉

Твой сайт: `https://golub-bozor.onrender.com`
Админка: `https://golub-bozor.onrender.com/admin/`

---

## ⚠️ ВАЖНО:
- Сервер засыпает через 15 минут
- Первая загрузка после сна ~30 сек
- Чтобы не засыпал: используй UptimeRobot (бесплатно)

## 🔄 Обновление сайта:
```powershell
git add .
git commit -m "Update"
git push
```
Render автоматически передеплоит!

---

📖 **Полная инструкция**: DEPLOY_INSTRUCTIONS.md
