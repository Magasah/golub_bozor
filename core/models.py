"""
Models for ZooBozor - Animal Marketplace
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _


# Listing type choices
LISTING_TYPE_CHOICES = [
    ('fixed', 'Фиксированная цена'),
    ('auction', 'Аукцион'),
]


class Animal(models.Model):
    """
    Model representing an animal listing on the marketplace
    """
    
    # CATEGORY CHOICES - Главная классификация
    CATEGORY_CHOICES = [
        ('cat', 'Кошки / Гурбаҳо'),
        ('dog', 'Собаки / Сагҳо'),
        ('parrot', 'Попугаи / Тӯтиҳо'),
        ('canary', 'Канарейки / Қанариҳо'),
        ('partridge', 'Кеклик / Кабкҳо'),
        ('chicken', 'Куры и Петухи / Мурғ ва Хурӯс'),
        ('pigeon', 'Голуби / Кафтарҳо'),
        ('rabbit', 'Кролики / Харгӯшҳо'),
        ('horse', 'Лошади / Аспҳо'),
        ('cow', 'Коровы / Говҳо'),
        ('goat', 'Козы / Бузҳо'),
        ('sheep', 'Бараны / Гӯсфандҳо'),
        ('fish', 'Рыбки / Моҳиҳо'),
        ('hamster', 'Хомяки / Хомякҳо'),
        ('turtle', 'Черепахи / Сангпуштҳо'),
        ('bird_other', 'Другие птицы / Паррандаҳои дигар'),
        ('reptile', 'Рептилии / Хазанда'),
        ('transport', 'Зоо-Такси / Ташвиқот'),
        ('other', 'Другие / Дигар'),
    ]
    
    # Gender choices
    GENDER_CHOICES = [
        ('male', 'Самец / Нар'),
        ('female', 'Самка / Мода'),
        ('pair', 'Пара / Ҷуфт'),
        ('unknown', 'Не указано'),
    ]
    
    # City choices
    CITY_CHOICES = [
        ('dushanbe', 'Душанбе'),
        ('khujand', 'Худжанд'),
        ('kulob', 'Куляб'),
        ('qurghonteppa', 'Курган-Тюбе'),
        ('hisor', 'Гисар'),
        ('istaravshan', 'Истаравшан'),
        ('tursunzoda', 'Турсунзаде'),
        ('khorog', 'Хорог'),
        ('vahdat', 'Вахдат'),
        ('panjakent', 'Пенджикент'),
        ('other', 'Другой город'),
    ]
    
    # ========== ОСНОВНЫЕ ПОЛЯ ==========
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='Категория',
        help_text='Вид животного',
        db_index=True
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название объявления'
    )
    
    description = models.TextField(
        verbose_name='Описание',
        help_text='Подробное описание животного'
    )
    
    # ========== ХАРАКТЕРИСТИКИ ЖИВОТНОГО ==========
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default='unknown',
        blank=True,
        verbose_name='Пол',
        help_text='Пол животного'
    )
    
    age = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Возраст',
        help_text='Например: 2 года, 6 месяцев, 1.5 года'
    )
    
    breed = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Порода',
        help_text='Порода животного (если есть)'
    )
    
    # ========== СПЕЦИФИЧНЫЕ ПОЛЯ ДЛЯ КАТЕГОРИЙ ==========
    
    # Для голубей (Pigeon)
    pigeon_breed = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Порода голубя',
        help_text='Например: Бойный, Статный, Николаевский'
    )
    
    flight_duration = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Длительность полета',
        help_text='Например: 2-3 часа, до 5 часов'
    )
    
    game_style = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Стиль игры/бой',
        help_text='Например: Столбовой бой, Ленточный'
    )
    
    GENDER_PIGEON_CHOICES = [
        ('male', 'Самец'),
        ('female', 'Самка'),
        ('pair', 'Пара'),
    ]
    
    gender_pigeon = models.CharField(
        max_length=20,
        choices=GENDER_PIGEON_CHOICES,
        blank=True,
        null=True,
        verbose_name='Пол (голубь)',
        help_text='Пол голубя или пара'
    )
    
    # Для скота (Cow, Sheep, Horse, Goat)
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Вес (кг)',
        help_text='Вес животного в килограммах'
    )
    
    livestock_breed = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Порода скота',
        help_text='Например: Абердин-ангус, Гиссарская, Ахалтекинская'
    )
    
    GENDER_LIVESTOCK_CHOICES = [
        ('male', 'Самец'),
        ('female', 'Самка'),
    ]
    
    gender_livestock = models.CharField(
        max_length=20,
        choices=GENDER_LIVESTOCK_CHOICES,
        blank=True,
        null=True,
        verbose_name='Пол (скот)',
        help_text='Пол животного'
    )
    
    # Для питомцев (Cat, Dog)
    pet_breed = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Порода питомца',
        help_text='Например: Британская, Персидская, Немецкая овчарка'
    )
    
    has_passport = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        verbose_name='Есть паспорт/прививки',
        help_text='Наличие ветеринарного паспорта'
    )
    
    # Для транспорта (Transport/Зоо-Такси)
    TRANSPORT_TYPE_CHOICES = [
        ('sprinter', 'Спринтер'),
        ('porter', 'Портер'),
        ('sedan', 'Легковая'),
        ('minivan', 'Минивэн'),
    ]
    
    transport_type = models.CharField(
        max_length=50,
        choices=TRANSPORT_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Тип авто',
        help_text='Тип транспорта для перевозки'
    )
    
    route_from = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Откуда',
        help_text='Откуда можно забрать животное'
    )
    
    route_to = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Куда',
        help_text='Куда доставляется животное'
    )
    
    # ========== ЦЕНЫ И ТИП ПРОДАЖИ ==========
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        help_text='Цена в сомони (TJS)'
    )
    
    listing_type = models.CharField(
        max_length=10,
        choices=LISTING_TYPE_CHOICES,
        default='fixed',
        verbose_name='Тип продажи',
        help_text='Аукцион доступен только для голубей'
    )
    
    # ========== АУКЦИОННЫЕ ПОЛЯ (только для голубей) ==========
    start_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Начальная цена (для аукциона)',
        help_text='Минимальная ставка для аукциона'
    )
    
    current_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Текущая цена',
        help_text='Обновляется автоматически при новых ставках'
    )
    
    auction_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата окончания аукциона'
    )
    
    is_sold = models.BooleanField(
        default=False,
        verbose_name='Продан'
    )
    
    winner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_animal_auctions',
        verbose_name='Победитель аукциона'
    )
    
    payment_receipt = models.ImageField(
        upload_to='receipts/',
        blank=True,
        null=True,
        verbose_name='Чек оплаты',
        help_text='Скриншот чека оплаты для аукциона (3 TJS)'
    )
    
    is_paid = models.BooleanField(
        default=False,
        verbose_name='Оплачено'
    )
    
    # ========== МЕДИА ==========
    main_photo = models.ImageField(
        upload_to='animals/%Y/%m/',
        verbose_name='Главное фото',
        help_text='Основное фото животного'
    )
    
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Видео (YouTube)',
        help_text='Ссылка на YouTube видео (необязательно)'
    )
    
    # ========== МЕСТОПОЛОЖЕНИЕ И КОНТАКТЫ ==========
    city = models.CharField(
        max_length=50,
        choices=CITY_CHOICES,
        default='dushanbe',
        verbose_name='Город',
        help_text='Город продавца',
        db_index=True
    )
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='animals',
        verbose_name='Владелец'
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        help_text='Контактный номер телефона'
    )
    
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='WhatsApp',
        help_text='Номер WhatsApp (например: +992900123456)'
    )
    
    telegram_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Telegram',
        help_text='Имя пользователя в Telegram (без @)'
    )
    
    # ========== СТАТУС И МЕТРИКИ ==========
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('sold', 'Продано'),
        ('archived', 'В архиве'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Статус',
        help_text='Статус объявления',
        db_index=True
    )
    
    is_vip = models.BooleanField(
        default=False,
        verbose_name='VIP размещение',
        help_text='Премиум размещение с золотой рамкой'
    )
    
    is_approved = models.BooleanField(
        default=False,
        verbose_name='Одобрено',
        help_text='Объявление прошло модерацию'
    )
    
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Просмотры',
        help_text='Количество просмотров объявления'
    )
    
    favorites = models.ManyToManyField(
        User,
        related_name='favorite_animals',
        blank=True,
        verbose_name='В избранном у',
        help_text='Пользователи, добавившие в избранное'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        db_index=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Животное'
        verbose_name_plural = 'Животные'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['city', 'category']),
        ]
    
    def clean(self):
        """
        ВАЛИДАЦИЯ: Аукцион доступен только для голубей
        """
        super().clean()
        
        # Проверка: аукцион только для голубей
        if self.listing_type == 'auction' and self.category != 'pigeon':
            raise ValidationError({
                'listing_type': 'Аукцион доступен только для категории "Голуби". '
                                'Для других животных выберите "Фиксированная цена".'
            })
        
        # Если аукцион - проверяем обязательные поля
        if self.listing_type == 'auction':
            if not self.start_price:
                raise ValidationError({
                    'start_price': 'Укажите начальную цену для аукциона.'
                })
            if not self.auction_end_date:
                raise ValidationError({
                    'auction_end_date': 'Укажите дату окончания аукциона.'
                })
            if self.auction_end_date and self.auction_end_date <= timezone.now():
                raise ValidationError({
                    'auction_end_date': 'Дата окончания должна быть в будущем.'
                })
    
    def save(self, *args, **kwargs):
        # Автоматически устанавливаем current_price из start_price для аукциона
        if self.listing_type == 'auction' and not self.current_price:
            self.current_price = self.start_price
        
        # Валидация перед сохранением
        self.full_clean()
        
        # Добавляем водяной знак на фото перед сохранением
        if self.main_photo:
            self._add_watermark()
        
        super().save(*args, **kwargs)
    
    def _add_watermark(self):
        """
        Добавить водяной знак "ZooBozor" на фото.
        Текст располагается в правом нижнем углу, полупрозрачный белый.
        """
        try:
            # Открываем изображение
            img = Image.open(self.main_photo)
            
            # Преобразуем в RGB если нужно (для JPEG)
            if img.mode in ('RGBA', 'LA'):
                # Создаем белый фон
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Создаем копию изображения и слой для текста
            watermarked = img.copy()
            txt_layer = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
            txt_draw = ImageDraw.Draw(txt_layer)
            
            # Пытаемся загрузить шрифт
            try:
                # Ищем шрифт в системе
                font_size = int(watermarked.width / 15)  # Размер относительно ширины
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 40)
                except:
                    # Используем стандартный шрифт если специальные недоступны
                    font = ImageFont.load_default()
            
            # Текст водяного знака
            watermark_text = "ZooBozor"
            
            # Получаем размеры текста
            bbox = txt_draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Позиция: правый нижний угол с отступом
            margin = 20
            x = watermarked.width - text_width - margin
            y = watermarked.height - text_height - margin
            
            # Рисуем текст с тенью (для читаемости)
            shadow_color = (0, 0, 0, 80)  # Черная полутень
            text_color = (255, 255, 255, 128)  # Белый полупрозрачный (50% opacity)
            
            # Тень
            txt_draw.text((x + 2, y + 2), watermark_text, font=font, fill=shadow_color)
            # Основной текст
            txt_draw.text((x, y), watermark_text, font=font, fill=text_color)
            
            # Объединяем слои
            watermarked = watermarked.convert('RGBA')
            watermarked = Image.alpha_composite(watermarked, txt_layer)
            watermarked = watermarked.convert('RGB')
            
            # Сохраняем в BytesIO
            output = BytesIO()
            watermarked.save(output, format='JPEG', quality=90)
            output.seek(0)
            
            # Заменяем содержимое поля
            file_name = self.main_photo.name
            self.main_photo.save(file_name, ContentFile(output.read()), save=False)
        
        except Exception as e:
            # Если ошибка - просто логируем и продолжаем без водяного знака
            print(f"Ошибка добавления водяного знака: {str(e)}")
            pass
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('animal_detail', kwargs={'pk': self.pk})
    
    def is_auction_active(self):
        """Проверка активности аукциона"""
        if self.listing_type != 'auction':
            return False
        if self.is_sold:
            return False
        if self.auction_end_date and self.auction_end_date <= timezone.now():
            return False
        return True
    
    def time_left(self):
        """Оставшееся время аукциона"""
        if not self.auction_end_date:
            return None
        delta = self.auction_end_date - timezone.now()
        if delta.total_seconds() <= 0:
            return "Завершён"
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}д {hours}ч"
        elif hours > 0:
            return f"{hours}ч {minutes}м"
        else:
            return f"{minutes}м"


class AnimalImage(models.Model):
    """
    Additional images for animal listings (gallery)
    """
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='gallery',
        verbose_name='Животное'
    )
    
    image = models.ImageField(
        upload_to='animals/gallery/%Y/%m/',
        verbose_name='Фото'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )
    
    class Meta:
        verbose_name = 'Фото животного'
        verbose_name_plural = 'Галерея фото'
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Фото для {self.animal.title}"


class Offer(models.Model):
    """
    Price offers from buyers (Smart Offer feature)
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]
    
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name='Животное'
    )
    
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='my_offers',
        verbose_name='Покупатель'
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Предложенная цена'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    
    message = models.TextField(
        blank=True,
        verbose_name='Сообщение',
        help_text='Опциональное сообщение от покупателя'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата предложения'
    )
    
    class Meta:
        verbose_name = 'Предложение цены'
        verbose_name_plural = 'Предложения цен'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.buyer.username} предлагает {self.price} TJS за {self.animal.title}"


class Bid(models.Model):
    """
    Auction bids for pigeon listings only
    """
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='bids',
        verbose_name='Животное (голубь)'
    )
    
    bidder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='animal_bids',
        verbose_name='Ставивший'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма ставки'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время ставки'
    )
    
    class Meta:
        verbose_name = 'Ставка'
        verbose_name_plural = 'Ставки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.bidder.username} - {self.amount} TJS"


class Veterinarian(models.Model):
    """
    Veterinary clinics and veterinarians directory
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название / Имя',
        help_text='Название клиники или имя ветеринара'
    )
    
    photo = models.ImageField(
        upload_to='veterinarians/',
        verbose_name='Фото',
        help_text='Фото клиники или врача'
    )
    
    description = models.TextField(
        verbose_name='Описание услуг',
        help_text='Подробное описание предоставляемых услуг'
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        help_text='Контактный номер телефона'
    )
    
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='WhatsApp',
        help_text='Номер WhatsApp'
    )
    
    city = models.CharField(
        max_length=50,
        choices=Animal.CITY_CHOICES,
        default='dushanbe',
        verbose_name='Город',
        help_text='Город расположения'
    )
    
    address = models.CharField(
        max_length=300,
        verbose_name='Адрес',
        help_text='Полный адрес клиники'
    )
    
    is_vip = models.BooleanField(
        default=False,
        verbose_name='VIP размещение',
        help_text='Премиум размещение с выделением'
    )
    
    is_approved = models.BooleanField(
        default=False,
        verbose_name='Одобрено',
        help_text='Запись прошла модерацию'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Ветеринар / Ветклиника'
        verbose_name_plural = 'Ветеринары и Ветклиники'
        ordering = ['-is_vip', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.city})"


# Keep existing models that don't need changes
class UserProfile(models.Model):
    """User profile with additional information"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Telegram Chat ID'
    )
    
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.00,
        verbose_name='Рейтинг'
    )
    
    total_sales = models.PositiveIntegerField(
        default=0,
        verbose_name='Всего продаж'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Верифицирован',
        help_text='Синяя галочка - доверенный продавец'
    )
    
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Баланс кошелька'),
        help_text=_('Баланс внутреннего кошелька в сомони (TJS)')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    def deduct_balance(self, amount):
        """
        Списать средства со счета пользователя.
        Создает запись в Transaction.
        
        Args:
            amount: Decimal - сумма к списанию
            
        Raises:
            ValueError: Если недостаточно средств
        """
        amount = Decimal(str(amount))
        
        if self.balance < amount:
            raise ValueError(
                f"Недостаточно средств. Баланс: {self.balance} TJS, "
                f"требуется: {amount} TJS"
            )
        
        self.balance -= amount
        self.save()
        
        # Создаем запись в Transaction
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='deduct',
            description='Списание со счета'
        )
    
    def add_balance(self, amount, description="Пополнение баланса"):
        """
        Пополнить баланс кошелька.
        
        Args:
            amount: Decimal - сумма пополнения
            description: str - описание пополнения
        """
        amount = Decimal(str(amount))
        self.balance += amount
        self.save()
        
        # Создаем запись в Transaction
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='add',
            description=description
        )


class Transaction(models.Model):
    """
    История транзакций для кошелька пользователя.
    Отслеживает все операции: пополнения, списания, платежи.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('add', _('Пополнение')),
        ('deduct', _('Списание')),
        ('payment', _('Платеж')),
        ('refund', _('Возврат')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('Пользователь')
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Сумма')
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name=_('Тип транзакции')
    )
    
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Описание'),
        help_text=_('Краткое описание причины транзакции')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата')
    )
    
    class Meta:
        verbose_name = _('Транзакция')
        verbose_name_plural = _('Транзакции')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.user.username} - {self.amount} TJS ({self.created_at.strftime('%d.%m.%Y')})"


class Review(models.Model):
    """Reviews for sellers"""
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        verbose_name='Продавец'
    )
    
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews',
        verbose_name='Покупатель'
    )
    
    rating = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        help_text='От 1 до 5'
    )
    
    comment = models.TextField(
        verbose_name='Комментарий'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата отзыва'
    )
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['seller', 'buyer'],
                name='no_self_review'
            )
        ]
    
    def __str__(self):
        return f"Отзыв от {self.buyer.username} для {self.seller.username}"


class Comment(models.Model):
    """Comments on animal listings"""
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Животное'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    
    text = models.TextField(
        verbose_name='Комментарий'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Комментарий от {self.author.username}"
