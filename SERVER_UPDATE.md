# 🚀 Обновление кода на PythonAnywhere

## Быстрая команда для обновления

Откройте **Bash console** на PythonAnywhere и выполните:

```bash
cd ~/golub_bozor
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
```

После этого нажмите зелёную кнопку **"Reload"** на вкладке Web.

---

## 📝 Пошаговая инструкция

### 1. Откройте Bash Console

Зайдите на https://www.pythonanywhere.com → Dashboard → **Consoles** → **Bash**

### 2. Перейдите в папку проекта

```bash
cd ~/golub_bozor
```

### 3. Проверьте текущее состояние

```bash
git status
git log --oneline -5
```

### 4. Получите последние изменения с GitHub

```bash
git pull origin main
```

Если будут конфликты с `.env`, выполните:

```bash
git checkout .env
git pull origin main
```

### 5. Активируйте виртуальное окружение

```bash
source venv/bin/activate
```

### 6. Обновите зависимости (если изменился requirements.txt)

```bash
pip install -r requirements.txt --upgrade
```

### 7. Примените миграции базы данных

```bash
python manage.py migrate
```

### 8. Создайте статьи энциклопедии (если ещё не созданы)

```bash
python populate_health.py
```

### 9. Соберите статические файлы

```bash
python manage.py collectstatic --no-input
```

### 10. Перезагрузите веб-приложение

Перейдите на вкладку **Web** → нажмите большую зелёную кнопку **"Reload magaj.pythonanywhere.com"**

---

## 🔧 Проверка после обновления

1. **Откройте сайт:** https://magaj.pythonanywhere.com
2. **Проверьте энциклопедию:** https://magaj.pythonanywhere.com/health/
3. **Проверьте админку:** https://magaj.pythonanywhere.com/admin/

Если есть ошибки, смотрите логи:

```bash
# В Bash console
tail -100 /var/log/magaj.pythonanywhere.com.error.log
```

Или на вкладке **Web** → **Log files** → **Error log**

---

## 🤖 Проверка Telegram бота

После обновления проверьте, что в `.env` на сервере есть:

```bash
cat .env | grep TELEGRAM
```

Должно быть:
```
TELEGRAM_BOT_TOKEN=8184229746:AAFIlY6d284Ti1-wqGrRi09-d97M1Xn2eYU
TELEGRAM_CHAT_ID=7828162060
```

Если нет, добавьте:

```bash
nano .env
```

Добавьте эти строки и сохраните (Ctrl+O, Enter, Ctrl+X)

---

## ⚡ Одна команда для всего

Создайте файл для быстрого обновления:

```bash
nano ~/update_site.sh
```

Вставьте:

```bash
#!/bin/bash
cd ~/golub_bozor
echo "📥 Получение изменений с GitHub..."
git pull origin main
source venv/bin/activate
echo "📦 Обновление зависимостей..."
pip install -r requirements.txt -q
echo "🗃️ Применение миграций..."
python manage.py migrate
echo "🖼️ Сбор статических файлов..."
python manage.py collectstatic --no-input
echo "✅ Готово! Теперь нажмите Reload на вкладке Web"
```

Сделайте исполняемым:

```bash
chmod +x ~/update_site.sh
```

Теперь для обновления просто запускайте:

```bash
~/update_site.sh
```

---

## 🆘 Решение проблем

### Ошибка "git pull" не работает

```bash
cd ~/golub_bozor
git reset --hard origin/main
git pull origin main
```

### Ошибка с миграциями

```bash
python manage.py migrate --fake-initial
```

### Ошибка с правами на файлы

```bash
chmod -R 755 ~/golub_bozor
```

### Сайт показывает старую версию

1. Очистите кеш браузера (Ctrl+Shift+R)
2. Проверьте, что нажали **Reload** на вкладке Web
3. Проверьте Error log на наличие ошибок

---

## 📞 Полезные ссылки

- Сайт: https://magaj.pythonanywhere.com
- Админка: https://magaj.pythonanywhere.com/admin/
- GitHub: https://github.com/Magasah/golub_bozor
- PythonAnywhere Dashboard: https://www.pythonanywhere.com/user/magaj/
