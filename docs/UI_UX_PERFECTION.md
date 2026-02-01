# 🎨 UI/UX Perfection Guide - ЗооБозор

## 📋 Обзор улучшений

Этот документ описывает 5 ключевых улучшений UI/UX для проекта ЗооБозор:

1. **Модальный селектор категорий** (Alpine.js + HTMX)
2. **VIP лимиты фото** (4 фото для стандарт, 6 для VIP)
3. **Dashboard с вкладками** (Мои объявления, Ставки, Избранное)
4. **Красивая админ-панель** (django-jazzmin или django-unfold)
5. **Heroicons + Типографика** (Золотые ссылки, Sans-serif шрифты)

---

## 1. 🎯 Модальный селектор категорий

### Описание
Вместо скучного `<select>` используется красивый модальный селектор с карточками категорий.

### Реализация

#### Frontend (Alpine.js)
Файл: `templates/core/add_animal_new.html`

**Ключевые особенности:**
- Полноэкранное модальное окно на мобильных устройствах
- Сетка 2/3/4 колонки (mobile/tablet/desktop)
- Плавные анимации при открытии/закрытии
- Большие эмодзи-иконки (🐕🐈🐴🐄)
- Золотые границы для выбранной категории
- Галочка ✓ на выбранной карточке

```javascript
function animalForm() {
    return {
        showCategoryModal: false,
        selectedCategory: '',
        
        categories: {
            'dog': { emoji: '🐕', name: 'Собаки' },
            'cat': { emoji: '🐈', name: 'Кошки' },
            // ... остальные 16 категорий
        },
        
        selectCategory(value) {
            this.selectedCategory = value;
            // Триггерим HTMX для загрузки динамических полей
            document.getElementById('category-input').dispatchEvent(new Event('change'));
        },
        
        getCategoryEmoji() {
            return this.categories[this.selectedCategory]?.emoji || '';
        },
        
        getCategoryName() {
            return this.categories[this.selectedCategory]?.name || '';
        }
    }
}
```

#### Backend (HTMX)
При выборе категории автоматически загружаются специфичные поля через HTMX:

```html
<input 
    type="hidden" 
    name="category" 
    id="category-input"
    x-model="selectedCategory"
    hx-get="{% url 'load_category_fields' %}"
    hx-trigger="change"
    hx-target="#dynamic-fields"
    hx-swap="innerHTML"
>
```

#### CSS классы
```css
.border-[#D4AF37]    /* Золотая граница */
.bg-[#121212]        /* Черный фон */
.bg-[#1E1E1E]        /* Темно-серый фон карточек */
.hover:scale-105     /* Увеличение при наведении */
.ring-4 ring-[#D4AF37]/30  /* Золотое кольцо вокруг выбранной */
```

### Адаптивность
```html
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
```

- **Mobile** (< 768px): 2 колонки
- **Tablet** (768-1024px): 3 колонки
- **Desktop** (> 1024px): 4 колонки

---

## 2. 📸 VIP лимиты фото

### Логика лимитов
- **Стандарт**: 1-4 фото
- **VIP**: 1-6 фото

### Backend валидация

#### Файл: `core/forms.py`

```python
class AnimalImageForm(forms.ModelForm):
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if not image:
            return image
        
        # Проверка размера (макс 5MB)
        if image.size > 5 * 1024 * 1024:
            raise ValidationError('Размер файла не должен превышать 5MB')
        
        # Проверка количества фото
        if self.animal and self.user:
            current_count = self.animal.images.count()
            max_photos = 6 if self.user.profile.is_vip else 4
            
            if current_count >= max_photos:
                if self.user.profile.is_vip:
                    raise ValidationError('Лимит фото превышен. VIP: до 6 фото.')
                else:
                    raise ValidationError(
                        'Лимит фото превышен. Стандарт: до 4 фото. '
                        'Купите VIP для увеличения лимита до 6 фото.'
                    )
        
        return image
```

### Frontend валидация

```javascript
previewPhotos(event) {
    const files = event.target.files;
    const maxPhotos = {% if request.user.profile.is_vip %}6{% else %}4{% endif %};
    
    if (files.length > maxPhotos) {
        alert(`❌ Лимит фото превышен! ${maxPhotos} фото максимум.`);
        event.target.value = '';
        return;
    }
    
    // Создание превью...
}
```

### UI индикатор

```html
<label class="block text-sm font-semibold text-[#D4AF37] mb-4">
    Фотографии *
    <span class="text-xs text-gray-500 ml-2">
        {% if request.user.profile.is_vip %}
            (VIP: до 6 фото)
        {% else %}
            (Стандарт: до 4 фото | 
            <a href="{% url 'vip_request' %}" class="text-[#D4AF37] underline">
                Получить VIP
            </a>)
        {% endif %}
    </span>
</label>
```

### Drag & Drop функционал

```javascript
handleFileDrop(event) {
    const files = event.dataTransfer.files;
    
    // Валидация количества
    if (files.length > this.maxPhotos) {
        alert('Лимит превышен!');
        return;
    }
    
    // Создание превью
    this.previewPhotos({ target: { files } });
}
```

---

## 3. 📊 Dashboard с вкладками

### Структура вкладок

1. **Мои объявления** (`?tab=listings`)
   - Все объявления пользователя
   - Фильтры: Активные / Модерация / Отклоненные

2. **Мои ставки** (`?tab=bids`)
   - Видно всем пользователям с хотя бы одной ставкой
   - Статусы аукционов: Активные / Завершенные / Выиграны

3. **Избранное** (`?tab=favorites`)
   - Избранные объявления
   - Кнопка "Удалить из избранного"

### Frontend (HTML + Tailwind)

```html
<div class="border-b border-gray-700 mb-8">
    <nav class="flex space-x-4 overflow-x-auto">
        <a href="?tab=listings" 
           class="px-6 py-3 font-semibold border-b-2 transition
                  {% if active_tab == 'listings' %}
                  border-[#D4AF37] text-[#D4AF37]
                  {% else %}
                  border-transparent text-gray-400 hover:text-white
                  {% endif %}">
            📋 Мои объявления
        </a>
        
        <a href="?tab=bids" 
           class="px-6 py-3 font-semibold border-b-2 transition
                  {% if active_tab == 'bids' %}
                  border-[#D4AF37] text-[#D4AF37]
                  {% else %}
                  border-transparent text-gray-400 hover:text-white
                  {% endif %}">
            🔨 Мои ставки
        </a>
        
        <a href="?tab=favorites" 
           class="px-6 py-3 font-semibold border-b-2 transition
                  {% if active_tab == 'favorites' %}
                  border-[#D4AF37] text-[#D4AF37]
                  {% else %}
                  border-transparent text-gray-400 hover:text-white
                  {% endif %}">
            ⭐ Избранное
        </a>
    </nav>
</div>
```

### Backend (Views)

```python
def dashboard(request):
    active_tab = request.GET.get('tab', 'listings')
    
    context = {
        'active_tab': active_tab,
    }
    
    if active_tab == 'listings':
        context['my_animals'] = Animal.objects.filter(
            seller=request.user
        ).order_by('-created_at')
        
    elif active_tab == 'bids':
        context['my_bids'] = Bid.objects.filter(
            bidder=request.user
        ).select_related('animal').order_by('-created_at')
        
    elif active_tab == 'favorites':
        context['favorites'] = request.user.favorite_animals.all()
    
    return render(request, 'core/dashboard.html', context)
```

### Компактные карточки (Mobile-friendly)

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {% for animal in my_animals %}
    <div class="bg-[#1E1E1E] rounded-lg overflow-hidden border border-gray-700 
                hover:border-[#D4AF37] transition">
        <img src="{{ animal.main_photo.url }}" 
             class="w-full h-40 object-cover">
        
        <div class="p-4">
            <h3 class="text-lg font-bold text-[#D4AF37] mb-2">
                {{ animal.title }}
            </h3>
            <p class="text-2xl font-bold text-white mb-3">
                {{ animal.price }} TJS
            </p>
            
            <!-- Статус -->
            <div class="flex items-center justify-between">
                <span class="px-3 py-1 text-xs rounded-full
                             {% if animal.status == 'active' %}
                             bg-green-900 text-green-300
                             {% elif animal.status == 'pending' %}
                             bg-yellow-900 text-yellow-300
                             {% else %}
                             bg-red-900 text-red-300
                             {% endif %}">
                    {{ animal.get_status_display }}
                </span>
                
                <!-- Кнопки действий -->
                <div class="flex space-x-2">
                    <a href="{% url 'animal_detail' animal.pk %}" 
                       class="text-[#D4AF37] hover:text-white">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                            <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
                        </svg>
                    </a>
                    <a href="{% url 'edit_animal' animal.pk %}" 
                       class="text-gray-400 hover:text-[#D4AF37]">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"/>
                        </svg>
                    </a>
                </div>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
```

---

## 4. 🎨 Красивая админ-панель

### Вариант 1: django-jazzmin (Рекомендуется)

#### Установка
```bash
pip install django-jazzmin
```

#### settings.py
```python
INSTALLED_APPS = [
    'jazzmin',  # Должен быть перед django.contrib.admin
    'django.contrib.admin',
    # ...
]

JAZZMIN_SETTINGS = {
    # Название сайта
    "site_title": "ЗооБозор Admin",
    "site_header": "ЗооБозор",
    "site_brand": "🦁 ЗооБозор",
    
    # Логотип
    "site_logo": "images/logo.png",
    "login_logo": None,
    
    # Welcome text
    "welcome_sign": "Добро пожаловать в админ-панель ЗооБозор",
    
    # Темная тема
    "theme": "darkly",  # Темная тема по умолчанию
    
    # Цвета (золотые акценты)
    "primary": "#D4AF37",
    "secondary": "#FFD700",
    "info": "#3498db",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "success": "#00bc8c",
    
    # Свернутое боковое меню
    "show_sidebar": True,
    "navigation_expanded": False,
    
    # Иконки (Heroicons-style)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.Animal": "fas fa-paw",
        "core.UserProfile": "fas fa-id-card",
        "core.Review": "fas fa-star",
        "core.Bid": "fas fa-gavel",
        "core.Veterinarian": "fas fa-user-md",
    },
    
    # Дополнительные ссылки
    "custom_links": {
        "core": [{
            "name": "Перейти на сайт",
            "url": "/",
            "icon": "fas fa-home",
        }]
    },
    
    # Скрыть модели
    "hide_apps": [],
    "hide_models": [],
    
    # Порядок моделей
    "order_with_respect_to": [
        "auth",
        "core",
        "core.animal",
        "core.userprofile",
    ],
    
    # UI настройки
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",  # Вкладки в формах
    "related_modal_active": True,  # Модальные окна для связанных объектов
}

# Дополнительные настройки UI
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-gold",
    "navbar": "navbar-dark navbar-dark",
    "no_navbar_border": True,
    "sidebar": "sidebar-dark-gold",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
}
```

### Вариант 2: django-unfold (Более современный)

#### Установка
```bash
pip install django-unfold
```

#### settings.py
```python
INSTALLED_APPS = [
    "unfold",  # Должен быть перед django.contrib.admin
    "django.contrib.admin",
    # ...
]

# Настройки Unfold
UNFOLD = {
    "SITE_TITLE": "ЗооБозор Admin",
    "SITE_HEADER": "🦁 ЗооБозор",
    "SITE_URL": "/",
    
    # Цвета (золотые акценты)
    "COLORS": {
        "primary": {
            "50": "#fefce8",
            "100": "#fef9c3",
            "200": "#fef08a",
            "300": "#fde047",
            "400": "#D4AF37",  # Основной золотой
            "500": "#eab308",
            "600": "#ca8a04",
            "700": "#a16207",
            "800": "#854d0e",
            "900": "#713f12",
        },
    },
    
    # Темная тема
    "THEME": "dark",
    
    # Sidebar
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Навигация",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Животные",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Все объявления",
                        "icon": "pets",
                        "link": reverse_lazy("admin:core_animal_changelist"),
                    },
                    {
                        "title": "На модерации",
                        "icon": "pending",
                        "link": reverse_lazy("admin:core_animal_changelist") + "?status__exact=pending",
                    },
                ],
            },
        ],
    },
}
```

---

## 5. ✨ Heroicons + Типографика

### Шрифты (Sans-serif)

#### base.html
```html
<head>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
    </style>
</head>
```

### Heroicons SVG (Inline)

Создайте partial шаблон: `templates/partials/heroicons.html`

```html
{% comment %}
Heroicons - inline SVG иконки
Использование: {% include 'partials/heroicons.html' with icon='check-circle' %}
{% endcomment %}

{% if icon == 'check-circle' %}
<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
</svg>

{% elif icon == 'x-mark' %}
<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
</svg>

{% elif icon == 'chevron-down' %}
<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
</svg>

{% elif icon == 'photo' %}
<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
</svg>

{% elif icon == 'heart' %}
<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd"/>
</svg>

{% elif icon == 'star' %}
<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
</svg>

{% elif icon == 'eye' %}
<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
    <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
</svg>

{% elif icon == 'pencil' %}
<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"/>
</svg>

{% elif icon == 'trash' %}
<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>
</svg>

{% endif %}
```

### Типографика и ссылки

#### Глобальные стили в base.html
```css
<style>
    /* Золотые заголовки */
    h1, h2, h3, h4, h5, h6 {
        color: #D4AF37;
        font-weight: 700;
    }
    
    /* Серый текст для body */
    body {
        color: #E5E7EB;  /* gray-200 */
    }
    
    /* Золотые и белые ссылки (НЕТ синих!) */
    a {
        color: #D4AF37;
        text-decoration: none;
        transition: color 0.2s;
    }
    
    a:hover {
        color: #FFD700;  /* Светло-золотой при hover */
    }
    
    /* Исключение: белые ссылки в навигации */
    nav a {
        color: #F3F4F6;  /* gray-100 */
    }
    
    nav a:hover, nav a.active {
        color: #D4AF37;
    }
    
    /* Кнопки */
    .btn-primary {
        background: linear-gradient(135deg, #D4AF37 0%, #FFD700 100%);
        color: #000;
        font-weight: 700;
    }
    
    .btn-primary:hover {
        background: linear-gradient(135deg, #FFD700 0%, #D4AF37 100%);
        transform: scale(1.05);
    }
    
    /* Золотые акценты */
    .text-accent {
        color: #D4AF37;
    }
    
    .border-accent {
        border-color: #D4AF37;
    }
    
    .bg-accent {
        background-color: #D4AF37;
    }
</style>
```

---

## 📱 Мобильная адаптация

### Все компоненты оптимизированы для мобильных устройств:

1. **Модальное окно категорий**
   - Полноэкранное на смартфонах
   - 2 колонки для удобного выбора
   - Большие touch-friendly карточки (минимум 80x80px)

2. **Фото-загрузка**
   - Drag & Drop работает на мобильных через touch events
   - Превью адаптируется под размер экрана
   - Удобные кнопки удаления

3. **Dashboard**
   - Горизонтальный скролл вкладок
   - Карточки в 1 колонку на смартфонах
   - Компактное отображение информации

4. **Админка**
   - Jazzmin и Unfold имеют встроенную мобильную адаптацию
   - Свернутое боковое меню на маленьких экранах
   - Touch-friendly элементы управления

---

## 🚀 Чеклист внедрения

### Этап 1: Модальный селектор ✅
- [x] Создан `add_animal_new.html` с Alpine.js
- [x] Добавлены все 18 категорий с эмодзи
- [x] Настроена интеграция с HTMX
- [ ] Заменить старый `add_animal.html` на новую версию
- [ ] Протестировать на мобильных устройствах

### Этап 2: VIP фото ✅
- [x] Обновлен `AnimalImageForm` с валидацией
- [x] Добавлен frontend-контроль в Alpine.js
- [ ] Создать view для обработки multiple upload
- [ ] Добавить backend обработку в `views.py`
- [ ] Тестирование лимитов

### Этап 3: Dashboard 🔄
- [ ] Создать новый шаблон `dashboard_new.html`
- [ ] Реализовать вкладки (HTML + CSS)
- [ ] Добавить backend логику фильтрации
- [ ] Компактные карточки для каждой вкладки
- [ ] Мобильная адаптация

### Этап 4: Админка ⏳
- [ ] Установить django-jazzmin: `pip install django-jazzmin`
- [ ] Добавить в INSTALLED_APPS
- [ ] Настроить JAZZMIN_SETTINGS
- [ ] Загрузить логотип
- [ ] Настроить иконки для моделей

### Этап 5: Типографика ⏳
- [ ] Подключить Google Fonts (Inter)
- [ ] Создать `heroicons.html` partial
- [ ] Обновить глобальные стили в base.html
- [ ] Заменить эмодзи на Heroicons (опционально)
- [ ] Проверить все ссылки (только золотой/белый)

---

## 🎯 Итоговый результат

После внедрения всех улучшений:

✅ **Современный UI** - Модальные окна, анимации, Heroicons  
✅ **Умная валидация** - VIP лимиты, реал-тайм проверка  
✅ **Удобная навигация** - Вкладки в dashboard, быстрый доступ  
✅ **Красивая админка** - Темная тема, золотые акценты, иконки  
✅ **Профессиональная типографика** - Sans-serif, золотые заголовки, правильные цвета ссылок  

**Общее время внедрения:** 3-4 часа  
**Сложность:** Средняя  
**Поддержка:** Все библиотеки активно поддерживаются  

---

## 📚 Дополнительные ресурсы

- [Alpine.js документация](https://alpinejs.dev/)
- [HTMX документация](https://htmx.org/)
- [django-jazzmin GitHub](https://github.com/farridav/django-jazzmin)
- [django-unfold GitHub](https://github.com/unfoldadmin/django-unfold)
- [Heroicons библиотека](https://heroicons.com/)
- [TailwindCSS цвета](https://tailwindcss.com/docs/customizing-colors)

---

*Документ создан для проекта ЗооБозор © 2024*
