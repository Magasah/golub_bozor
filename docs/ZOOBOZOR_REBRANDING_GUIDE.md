# 🦁 ZOOBOZOR REBRANDING - ПОЛНАЯ ИНСТРУКЦИЯ ПО ВНЕДРЕНИЮ

## 📋 ЧТО БЫЛО СДЕЛАНО

### ✅ 1. СОЗДАНЫ НОВЫЕ ФАЙЛЫ:

**Модели:**
- `core/models_new.py` - Новая модель Animal с категориями, Veterinarian, удалена HealthGuide

**Views:**
- `core/views_new.py` - Обновленные views для Animal и Veterinarian

**Forms:**
- `core/forms_new.py` - Новые формы с фильтрами по категориям

**Signals:**
- `core/signals_new.py` - Telegram уведомления с эмодзи по категориям

**Templates (Восстановление пароля):**
- `templates/registration/password_reset_form.html`
- `templates/registration/password_reset_done.html`
- `templates/registration/password_reset_confirm.html`
- `templates/registration/password_reset_complete.html`

**JavaScript:**
- `static/js/auction_toggle.js` - Блокировка аукционов для не-голубей

**Инструкции:**
- `EMAIL_SETTINGS_ADD_TO_SETTINGS.txt` - Настройки SMTP для восстановления пароля

---

## 🚀 ПОШАГОВОЕ ВНЕДРЕНИЕ

### ШАГ 1: РЕЗЕРВНОЕ КОПИРОВАНИЕ

```bash
# Создайте резервную копию базы данных
cp db.sqlite3 db.sqlite3.backup

# Создайте резервную копию старых файлов
cp core/models.py core/models_old.py
cp core/views.py core/views_old.py
cp core/forms.py core/forms_old.py
cp core/signals.py core/signals_old.py
```

### ШАГ 2: ЗАМЕНА ОСНОВНЫХ ФАЙЛОВ

```bash
# Замените старые файлы новыми
mv core/models_new.py core/models.py
mv core/views_new.py core/views.py
mv core/forms_new.py core/forms.py
mv core/signals_new.py core/signals.py
```

### ШАГ 3: ОБНОВИТЕ settings.py

Откройте `config/settings.py` и добавьте в КОНЕЦ файла:

```python
# ========== EMAIL CONFIGURATION ==========
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Для тестирования (консоль)
if DEBUG and not EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

PASSWORD_RESET_TIMEOUT = 3600
```

### ШАГ 4: ОБНОВИТЕ urls.py

Откройте `core/urls.py` и замените:

**Старые URL:**
```python
path('', views.home, name='home'),
path('pigeon/<int:pk>/', views.pigeon_detail, name='pigeon_detail'),
path('add/', views.add_pigeon, name='add_pigeon'),
path('health/', views.health_list, name='health_list'),
```

**Новые URL:**
```python
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Главная и животные
    path('', views.home, name='home'),
    path('animal/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('animal/add/', views.add_animal, name='add_animal'),
    path('animal/<int:pk>/edit/', views.edit_animal, name='edit_animal'),
    path('animal/<int:pk>/delete/', views.delete_animal, name='delete_animal'),
    path('my-animals/', views.my_animals, name='my_animals'),
    
    # Ветеринары (заменяет Health)
    path('veterinarians/', views.veterinarians_list, name='veterinarians_list'),
    path('veterinarian/<int:pk>/', views.veterinarian_detail, name='veterinarian_detail'),
    path('veterinarian/add/', views.add_veterinarian, name='add_veterinarian'),
    
    # Аукционы и избранное
    path('animal/<int:pk>/bid/', views.place_bid, name='place_bid'),
    path('animal/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites, name='favorites'),
    
    # Комментарии
    path('animal/<int:pk>/comment/', views.add_comment, name='add_comment'),
    
    # Профиль
    path('profile/<str:username>/', views.profile, name='profile'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Восстановление пароля
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]
```

### ШАГ 5: ОБНОВИТЕ apps.py

Откройте `core/apps.py`:

```python
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        import core.signals  # Импорт сигналов
```

### ШАГ 6: ОБНОВИТЕ HTML ШАБЛОНЫ

**В templates/base.html найдите и замените:**

1. Все `"GolubBozor"` → `"ZooBozor"`
2. Все `"Голубь Бозор"` → `"Zoo Bozor"`
3. В меню замените:
   ```html
   <!-- Старое -->
   <a href="{% url 'health_list' %}">📚 Лечение</a>
   
   <!-- Новое -->
   <a href="{% url 'veterinarians_list' %}">🏥 Ветеринары</a>
   ```

4. В кнопке "Добавить":
   ```html
   <!-- Старое -->
   <a href="{% url 'add_pigeon' %}">+ Добавить голубя</a>
   
   <!-- Новое -->
   <a href="{% url 'add_animal' %}">+ Добавить объявление</a>
   ```

### ШАГ 7: ДОБАВЬТЕ JavaScript В ШАБЛОН ДОБАВЛЕНИЯ

В `templates/core/add_animal.html` (или создайте новый):

```html
{% extends 'base.html' %}
{% load static %}

{% block extra_js %}
<script src="{% static 'js/auction_toggle.js' %}"></script>
{% endblock %}
```

### ШАГ 8: МИГРАЦИИ БАЗЫ ДАННЫХ

```bash
# Создайте миграции
python manage.py makemigrations

# Примените миграции
python manage.py migrate
```

**ВАЖНО:** Django может предложить создать миграции для переименования модели. Выберите:
- `Did you rename pigeon.Pigeon to core.Animal? [y/N]` → **N** (Нет)

Это создаст новую модель Animal отдельно от Pigeon.

### ШАГ 9: ПЕРЕНОС ДАННЫХ (если нужно)

Если хотите сохранить старые данные голубей, создайте скрипт миграции:

```bash
python manage.py shell
```

```python
from core.models import Pigeon, Animal

# Перенос голубей в Animal
for pigeon in Pigeon.objects.all():
    Animal.objects.create(
        category='pigeon',
        title=pigeon.title,
        description=pigeon.description,
        gender=pigeon.sex,  # переименование поля
        breed=pigeon.breed,
        price=pigeon.price,
        listing_type=pigeon.listing_type,
        main_photo=pigeon.image,  # переименование поля
        city=pigeon.city,
        owner=pigeon.owner,
        phone=pigeon.phone,
        whatsapp_number=pigeon.whatsapp_number,
        telegram_username=pigeon.telegram_username,
        is_vip=pigeon.is_vip,
        is_approved=pigeon.is_approved,
        views_count=pigeon.views_count,
        created_at=pigeon.created_at,
        updated_at=pigeon.updated_at,
        # Аукционные поля
        start_price=pigeon.start_price,
        current_price=pigeon.current_price,
        auction_end_date=pigeon.auction_end_date,
        is_sold=pigeon.is_sold,
        winner=pigeon.winner,
        payment_receipt=pigeon.payment_receipt,
        is_paid=pigeon.is_paid,
    )

print(f"✅ Перенесено {Animal.objects.count()} животных")
```

### ШАГ 10: ОБНОВИТЕ ADMIN

Откройте `core/admin.py` и обновите:

```python
from django.contrib import admin
from .models import Animal, AnimalImage, Veterinarian, Bid, Review, Comment, UserProfile

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'city', 'owner', 'is_approved', 'is_vip', 'created_at']
    list_filter = ['category', 'is_approved', 'is_vip', 'city', 'listing_type']
    search_fields = ['title', 'description', 'breed']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'title', 'description')
        }),
        ('Характеристики', {
            'fields': ('gender', 'age', 'breed')
        }),
        ('Цена и тип продажи', {
            'fields': ('price', 'listing_type', 'start_price', 'current_price', 'auction_end_date', 'is_sold', 'winner')
        }),
        ('Медиа', {
            'fields': ('main_photo', 'video_url')
        }),
        ('Контакты и местоположение', {
            'fields': ('owner', 'phone', 'whatsapp_number', 'telegram_username', 'city')
        }),
        ('Статус', {
            'fields': ('is_approved', 'is_vip', 'views_count')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Veterinarian)
class VeterinarianAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'is_vip', 'is_approved', 'created_at']
    list_filter = ['city', 'is_vip', 'is_approved']
    search_fields = ['name', 'description', 'address']

# Остальные модели...
```

### ШАГ 11: ОБНОВИТЕ .env

Добавьте в `.env`:

```env
# Email для восстановления пароля
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=ZooBozor <your-email@gmail.com>
```

### ШАГ 12: ТЕСТИРОВАНИЕ

```bash
# Запустите сервер
python manage.py runserver

# Проверьте:
# 1. http://127.0.0.1:8000/ - главная страница
# 2. http://127.0.0.1:8000/animal/add/ - добавление (проверьте блокировку аукциона)
# 3. http://127.0.0.1:8000/veterinarians/ - ветеринары
# 4. http://127.0.0.1:8000/password-reset/ - восстановление пароля
# 5. http://127.0.0.1:8000/admin/ - админка
```

### ШАГ 13: GIT COMMIT

```bash
git add .
git commit -m "Rebranding: GolubBozor → ZooBozor

- Renamed Pigeon model to Animal with 13 categories
- Removed HealthGuide, added Veterinarian model
- Updated all views, forms, and signals
- Added password reset functionality with styled templates
- Auction restriction: only pigeons can use auctions
- Category-based Telegram notifications with emojis
- New filtering system by category, city, gender, price
- JavaScript validation for auction fields"

git push origin main
```

---

## 🎯 КЛЮЧЕВЫЕ ОСОБЕННОСТИ

### ✅ Валидация аукционов
- Аукционы доступны **ТОЛЬКО** для категории "Голуби" (pigeon)
- JavaScript автоматически блокирует выбор аукциона для других категорий
- Django валидация в методе `clean()` модели Animal

### ✅ Telegram уведомления
- Каждая категория имеет свою эмодзи:
  - 🐈 Кошки
  - 🐕 Собаки
  - 🕊️ Голуби
  - 🐎 Лошади
  - и т.д.

### ✅ Фильтры
- Категория (главный фильтр)
- Город
- Пол
- Цена (от/до)
- Тип продажи (фикс/аукцион)

### ✅ Восстановление пароля
- Стильные шаблоны в черно-золотом дизайне
- Настройка SMTP через .env
- Консольный режим для разработки

---

## 📞 ПОМОЩЬ

Если что-то не работает:

1. **Ошибки миграций:** `python manage.py migrate --fake-initial`
2. **Старые данные:** Используйте скрипт переноса из Шага 9
3. **Email не работает:** Проверьте настройки Gmail App Password
4. **Аукционы не блокируются:** Убедитесь что `auction_toggle.js` подключен в шаблоне

---

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ

- [ ] models.py заменён
- [ ] views.py заменён
- [ ] forms.py заменён
- [ ] signals.py заменён
- [ ] urls.py обновлён
- [ ] admin.py обновлён
- [ ] settings.py обновлён (EMAIL настройки)
- [ ] base.html обновлён (GolubBozor → ZooBozor)
- [ ] auction_toggle.js добавлен и подключен
- [ ] Шаблоны password_reset созданы
- [ ] .env обновлён (EMAIL переменные)
- [ ] Миграции применены
- [ ] Данные перенесены (если нужно)
- [ ] Тестирование пройдено
- [ ] Git push выполнен

---

**🎉 ГОТОВО! ZOOBOZOR ЗАПУЩЕН!**
