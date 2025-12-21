# 🎨 ДИЗАЙН-СИСТЕМА - GolubBozor Dark Luxury Theme

## 📐 Цветовая палитра

### Основные цвета
```css
/* Фоны */
--bg-primary: #121212       /* Основной фон страницы */
--bg-secondary: #1E1E1E     /* Фон карточек и модальных окон */

/* Акценты */
--gold: #D4AF37             /* Золотой акцент (кнопки, заголовки, рамки) */
--gold-hover: #C5A028       /* Золотой при наведении */

/* Текст */
--text-primary: #E5E5E5     /* Основной текст */
--text-secondary: #9CA3AF   /* Вторичный текст */
--text-muted: #6B7280       /* Приглушенный текст */

/* Границы */
--border-default: #374151   /* Обычные границы */
--border-gold: #D4AF37      /* Золотые границы */
```

### Tailwind классы
```
Фон: bg-[#121212], bg-[#1E1E1E]
Текст: text-gray-200, text-gray-400, text-[#D4AF37]
Границы: border-gray-700, border-gray-800, border-[#D4AF37]
```

---

## 🔤 Типографика

### Шрифты
```html
<!-- Google Fonts -->
Playfair Display - serif (для заголовков h1-h6)
Inter - sans-serif (для основного текста)
```

### Применение
```css
body {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif;
}
```

### Размеры заголовков
- h1: `text-5xl` (48px) - Главная страница
- h2: `text-4xl` (36px) - Заголовки разделов
- h3: `text-3xl` (30px) - Цены
- h4: `text-2xl` (24px) - Карточки товаров

---

## 🎯 Компоненты

### 1. Кнопки

#### Primary Button (Золотая)
```html
<button class="px-6 py-3 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#C5A028] transition">
    Текст кнопки
</button>
```

#### Secondary Button (Обводка)
```html
<button class="px-6 py-3 border-2 border-[#D4AF37] text-[#D4AF37] font-semibold rounded-lg hover:bg-[#D4AF37] hover:text-black transition">
    Текст кнопки
</button>
```

#### Danger Button (Красная)
```html
<button class="px-6 py-3 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700 transition">
    Удалить
</button>
```

---

### 2. Карточки товаров

#### Обычная карточка
```html
<div class="bg-[#1E1E1E] rounded-lg overflow-hidden border border-gray-800 hover:transform hover:scale-105 transition-all">
    <!-- Контент -->
</div>
```

#### VIP карточка
```html
<div class="bg-[#1E1E1E] rounded-lg overflow-hidden border-4 border-[#D4AF37] shadow-lg shadow-[#D4AF37]/20">
    <div class="bg-[#D4AF37] text-black text-center py-1 font-semibold text-sm">
        ⭐ VIP ОБЪЯВЛЕНИЕ ⭐
    </div>
    <!-- Контент -->
</div>
```

---

### 3. Формы

#### Input поле
```html
<input 
    type="text" 
    class="w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none"
    placeholder="Текст..."
>
```

#### Textarea
```html
<textarea 
    class="w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none"
    rows="6"
></textarea>
```

#### Checkbox
```html
<input 
    type="checkbox" 
    class="w-5 h-5 text-[#D4AF37] bg-[#1E1E1E] border-gray-700 rounded focus:ring-[#D4AF37]"
>
```

#### Label
```html
<label class="block text-sm font-semibold text-[#D4AF37] mb-2">
    Название поля
</label>
```

---

### 4. Навигация

#### Navbar
```html
<nav class="bg-[#1E1E1E] border-b border-gray-800 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <!-- Контент -->
        </div>
    </div>
</nav>
```

#### Навигационные ссылки
```html
<a href="#" class="text-gray-300 hover:text-[#D4AF37] transition">
    Ссылка
</a>
```

---

### 5. Алерты/Сообщения

#### Success
```html
<div class="p-4 rounded-lg bg-green-900 border border-green-700">
    Успешное сообщение
</div>
```

#### Error
```html
<div class="p-4 rounded-lg bg-red-900 border border-red-700">
    Ошибка
</div>
```

#### Info
```html
<div class="p-4 rounded-lg bg-blue-900 border border-blue-700">
    Информация
</div>
```

---

### 6. Значки и бейджи

#### VIP Badge
```html
<div class="bg-[#D4AF37] text-black text-center py-1 font-semibold text-sm">
    ⭐ VIP ОБЪЯВЛЕНИЕ ⭐
</div>
```

#### Цена
```html
<span class="text-3xl font-bold gold-text">1000</span>
<span class="text-gray-400 ml-1">TJS</span>
```

---

## 📱 Адаптивность

### Breakpoints (Tailwind)
```
sm:  640px   - Мобильные (большие)
md:  768px   - Планшеты
lg:  1024px  - Десктоп (маленький)
xl:  1280px  - Десктоп (большой)
```

### Grid система
```html
<!-- 1 колонка на мобильных, 2 на планшетах, 3 на десктопе -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

### Скрытие элементов
```html
<!-- Показывать только на мобильных -->
<div class="block md:hidden">Мобильная версия</div>

<!-- Скрывать на мобильных -->
<div class="hidden md:block">Десктоп версия</div>
```

---

## 🎭 Анимации и эффекты

### Hover эффект для карточек
```html
hover:transform hover:scale-105 transition-all duration-300
```

### Тень для VIP карточек
```html
shadow-lg shadow-[#D4AF37]/20
```

### Transition для ссылок
```html
transition  /* Плавный переход всех свойств */
```

---

## 🏗️ Layout структура

### Контейнер страницы
```html
<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Контент -->
</main>
```

### 2-колоночный layout (детальная страница)
```html
<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
    <div class="lg:col-span-2">
        <!-- Левая колонка (основной контент) -->
    </div>
    <div class="lg:col-span-1">
        <!-- Правая колонка (сайдбар) -->
    </div>
</div>
```

---

## 📐 Spacing (Отступы)

### Padding
- Маленький: `p-4` (16px)
- Средний: `p-6` (24px)
- Большой: `p-8` (32px)

### Margin
- Между элементами: `mb-4`, `mb-6`, `mb-8`
- Между секциями: `my-8`, `my-12`, `my-16`

### Gap (для Grid/Flex)
- Стандартный: `gap-6` (24px)

---

## 🖼️ Изображения

### Превью в карточках
```html
<img 
    src="..." 
    alt="..." 
    class="w-full h-64 object-cover"
>
```

### Полноразмерное изображение
```html
<img 
    src="..." 
    alt="..." 
    class="w-full h-auto"
>
```

---

## 🎬 YouTube Embed

```html
<div class="aspect-w-16 aspect-h-9 bg-gray-900 rounded-lg overflow-hidden">
    <iframe 
        src="https://www.youtube.com/embed/VIDEO_ID" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen
        class="w-full h-96"
    ></iframe>
</div>
```

---

## 🔍 Иконки (Heroicons SVG)

### Пример: Поиск
```html
<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[#D4AF37]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
</svg>
```

Все иконки: [Heroicons](https://heroicons.com/)

---

## 🎨 Кастомные CSS классы

```css
.gold-text {
    color: #D4AF37;
}

.gold-border {
    border-color: #D4AF37;
}

.gold-bg {
    background-color: #D4AF37;
}
```

---

**ГолубБозор © 2025 - Dark Luxury Design System**
