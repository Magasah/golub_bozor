# 🐍 ПРИМЕРЫ КОДА - GolubBozor

## Django Shell примеры

### Запуск Django Shell
```bash
python manage.py shell
```

---

## 📝 Создание объектов

### 1. Создать пользователя
```python
from django.contrib.auth.models import User

# Создать обычного пользователя
user = User.objects.create_user(
    username='aziz_dushanbe',
    email='aziz@example.com',
    password='mypassword123'
)

# Создать суперпользователя
admin = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)
```

### 2. Создать объявление голубя
```python
from core.models import Pigeon
from django.contrib.auth.models import User

# Получить пользователя
owner = User.objects.first()

# Создать голубя
pigeon = Pigeon.objects.create(
    title='Бойный голубь Тегеранский',
    price=5000.00,
    description='Редкий бойный голубь из Ирана. Возраст 2 года, отличные летные качества.',
    phone='+992 900 123 456',
    owner=owner,
    is_vip=True  # VIP размещение
)
# Примечание: image нужно загрузить через форму или вручную
```

### 3. Создать голубя с изображением
```python
from core.models import Pigeon
from django.core.files import File

pigeon = Pigeon(
    title='Декоративный голубь',
    price=3000.00,
    description='Красивый декоративный голубь',
    phone='+992 900 111 222',
    owner=owner
)

# Загрузить изображение
with open('path/to/image.jpg', 'rb') as f:
    pigeon.image.save('pigeon.jpg', File(f), save=True)
```

---

## 🔍 Запросы (Queries)

### Получить все объявления
```python
from core.models import Pigeon

# Все голуби
all_pigeons = Pigeon.objects.all()

# Только VIP
vip_pigeons = Pigeon.objects.filter(is_vip=True)

# Сортировка по цене
cheap_to_expensive = Pigeon.objects.order_by('price')
expensive_to_cheap = Pigeon.objects.order_by('-price')

# Последние 5 объявлений
recent = Pigeon.objects.order_by('-created_at')[:5]
```

### Поиск
```python
from django.db.models import Q

# Поиск по названию
results = Pigeon.objects.filter(title__icontains='бойный')

# Поиск по описанию
results = Pigeon.objects.filter(description__icontains='редкий')

# Поиск по названию ИЛИ описанию
results = Pigeon.objects.filter(
    Q(title__icontains='голубь') | 
    Q(description__icontains='голубь')
)

# Диапазон цен
results = Pigeon.objects.filter(price__gte=1000, price__lte=5000)
```

### Фильтрация по пользователю
```python
# Все объявления конкретного пользователя
user_pigeons = Pigeon.objects.filter(owner__username='aziz_dushanbe')

# Или через связь
user = User.objects.get(username='aziz_dushanbe')
user_pigeons = user.pigeons.all()  # reverse relation
```

### Агрегация и аннотация
```python
from django.db.models import Count, Avg, Max, Min

# Количество объявлений
total = Pigeon.objects.count()
vip_count = Pigeon.objects.filter(is_vip=True).count()

# Средняя цена
avg_price = Pigeon.objects.aggregate(Avg('price'))
# {'price__avg': 3500.0}

# Минимальная и максимальная цена
price_range = Pigeon.objects.aggregate(
    min_price=Min('price'),
    max_price=Max('price')
)
# {'min_price': 1000.0, 'max_price': 10000.0}

# Количество объявлений каждого пользователя
from django.contrib.auth.models import User
users_with_counts = User.objects.annotate(
    pigeon_count=Count('pigeons')
)
```

---

## ✏️ Обновление объектов

### Обновить одно объявление
```python
pigeon = Pigeon.objects.get(id=1)
pigeon.price = 6000.00
pigeon.is_vip = True
pigeon.save()
```

### Массовое обновление
```python
# Сделать все объявления дешевле 1000 VIP
Pigeon.objects.filter(price__lt=1000).update(is_vip=True)

# Убрать VIP у старых объявлений
from datetime import datetime, timedelta
old_date = datetime.now() - timedelta(days=30)
Pigeon.objects.filter(created_at__lt=old_date).update(is_vip=False)
```

---

## ❌ Удаление объектов

### Удалить одно объявление
```python
pigeon = Pigeon.objects.get(id=1)
pigeon.delete()
```

### Массовое удаление
```python
# Удалить все объявления без VIP
Pigeon.objects.filter(is_vip=False).delete()

# Удалить старые объявления
Pigeon.objects.filter(created_at__lt=old_date).delete()
```

---

## 🔗 Работа со связями

### Получить владельца
```python
pigeon = Pigeon.objects.get(id=1)
owner = pigeon.owner
print(owner.username, owner.email)
```

### Получить все объявления пользователя
```python
user = User.objects.get(username='aziz_dushanbe')
his_pigeons = user.pigeons.all()  # related_name='pigeons'
```

### Выборка с связанными данными (оптимизация)
```python
# Без оптимизации (N+1 запросов)
pigeons = Pigeon.objects.all()
for p in pigeons:
    print(p.owner.username)  # каждый раз запрос к БД

# С оптимизацией (2 запроса)
pigeons = Pigeon.objects.select_related('owner').all()
for p in pigeons:
    print(p.owner.username)  # данные уже загружены
```

---

## 🎥 Работа с YouTube URL

### Получить embed URL
```python
pigeon = Pigeon.objects.get(id=1)
embed_url = pigeon.get_youtube_embed_url()
# Возвращает: 'https://www.youtube.com/embed/VIDEO_ID' или None
```

### Установить YouTube URL
```python
pigeon.video_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
pigeon.save()

# Или короткая ссылка
pigeon.video_url = 'https://youtu.be/dQw4w9WgXcQ'
pigeon.save()
```

---

## 📊 Сложные запросы

### VIP голуби конкретного пользователя
```python
vip_user_pigeons = Pigeon.objects.filter(
    owner__username='aziz_dushanbe',
    is_vip=True
)
```

### Голуби с видео
```python
pigeons_with_video = Pigeon.objects.exclude(video_url__isnull=True).exclude(video_url='')
```

### Самые дорогие VIP объявления
```python
top_vip = Pigeon.objects.filter(is_vip=True).order_by('-price')[:10]
```

### Пользователи с VIP объявлениями
```python
vip_users = User.objects.filter(pigeons__is_vip=True).distinct()
```

---

## 🧪 Тестовые данные (fixtures)

### Создать тестовые данные
```python
from core.models import Pigeon
from django.contrib.auth.models import User

# Создать тестового пользователя
user = User.objects.create_user(
    username='test_user',
    email='test@example.com',
    password='test123'
)

# Создать тестовые объявления
test_pigeons = [
    {
        'title': 'Бойный голубь №1',
        'price': 3000,
        'description': 'Тестовое описание 1',
        'phone': '+992 900 111 111',
        'is_vip': True
    },
    {
        'title': 'Декоративный голубь №2',
        'price': 2000,
        'description': 'Тестовое описание 2',
        'phone': '+992 900 222 222',
        'is_vip': False
    },
    {
        'title': 'Почтовый голубь №3',
        'price': 4000,
        'description': 'Тестовое описание 3',
        'phone': '+992 900 333 333',
        'is_vip': True
    },
]

for data in test_pigeons:
    Pigeon.objects.create(owner=user, **data)
```

---

## 🛠️ Утилиты

### Проверка существования
```python
# Проверить, существует ли голубь
exists = Pigeon.objects.filter(id=1).exists()

# Получить или создать
pigeon, created = Pigeon.objects.get_or_create(
    title='Уникальный голубь',
    defaults={
        'price': 5000,
        'description': 'Описание',
        'phone': '+992 900 000 000',
        'owner': user
    }
)
```

### Получить объект или 404
```python
from django.shortcuts import get_object_or_404

# В views.py
pigeon = get_object_or_404(Pigeon, id=1)
```

### Подсчет
```python
# Количество VIP
vip_count = Pigeon.objects.filter(is_vip=True).count()

# Количество объявлений пользователя
user_count = Pigeon.objects.filter(owner=user).count()
```

---

## 🔄 Транзакции

```python
from django.db import transaction

# Атомарная операция
with transaction.atomic():
    pigeon = Pigeon.objects.create(...)
    pigeon.is_vip = True
    pigeon.save()
    # Если произойдет ошибка, все откатится
```

---

## 📅 Работа с датами

```python
from datetime import datetime, timedelta
from django.utils import timezone

# Объявления за последнюю неделю
week_ago = timezone.now() - timedelta(days=7)
recent = Pigeon.objects.filter(created_at__gte=week_ago)

# Объявления сегодня
today = timezone.now().date()
today_pigeons = Pigeon.objects.filter(created_at__date=today)

# Объявления за конкретный месяц
january = Pigeon.objects.filter(
    created_at__year=2025,
    created_at__month=1
)
```

---

## 💾 Экспорт/Импорт данных

### Экспорт в JSON
```bash
python manage.py dumpdata core.Pigeon --indent 2 > pigeons.json
```

### Импорт из JSON
```bash
python manage.py loaddata pigeons.json
```

---

## 🎯 Практические примеры

### Топ-10 самых дорогих голубей
```python
top_expensive = Pigeon.objects.order_by('-price')[:10]
for p in top_expensive:
    print(f"{p.title}: {p.price} TJS")
```

### Все VIP объявления с видео
```python
vip_with_video = Pigeon.objects.filter(
    is_vip=True
).exclude(video_url__isnull=True).exclude(video_url='')
```

### Статистика по пользователям
```python
from django.db.models import Count, Avg

stats = User.objects.annotate(
    total_pigeons=Count('pigeons'),
    vip_pigeons=Count('pigeons', filter=Q(pigeons__is_vip=True)),
    avg_price=Avg('pigeons__price')
).filter(total_pigeons__gt=0)

for user in stats:
    print(f"{user.username}: {user.total_pigeons} объявлений, средняя цена: {user.avg_price}")
```

---

**🐍 Эти примеры помогут вам работать с Django ORM в проекте GolubBozor!**
