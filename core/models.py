"""
Models for GolubBozor - Pigeon Marketplace
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


# Auction system: listing type choices
LISTING_TYPE_CHOICES = [
    ('fixed', 'Фиксированная цена'),
    ('auction', 'Аукцион'),
]


class Pigeon(models.Model):
    """
    Model representing a pigeon listing on the marketplace
    """
    
    # Breed choices (Extended list for better variety)
    BREED_CHOICES = [
        ('lailaki', 'Лайлаки'),
        ('sochi', 'Сочи'),
        ('chinny', 'Чинны'),
        ('sych', 'Сыч'),
        ('zhuk', 'Жук'),
        ('mallya', 'Малля'),
        ('kukcha', 'Кукча'),
        ('tajik_highflyer', 'Таджикский Лётный'),
        ('two_crested', 'Двухчубый'),
        ('tugma', 'Тугма'),
        ('metis', 'Метис'),
        ('other', 'Другая'),
    ]
    
    # Game type choices
    GAME_TYPE_CHOICES = [
        ('flight', 'Только полет'),
        ('game', 'Бойные/Игровые'),
        ('decoration', 'Декоративные'),
    ]
    
    # Sex choices
    SEX_CHOICES = [
        ('male', 'Самец'),
        ('female', 'Самка'),
        ('pair', 'Пара'),
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
    
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название голубя/объявления'
    )
    
    breed = models.CharField(
        max_length=50,
        choices=BREED_CHOICES,
        default='other',
        verbose_name='Порода',
        help_text='Порода голубя'
    )
    
    game_type = models.CharField(
        max_length=50,
        choices=GAME_TYPE_CHOICES,
        default='flight',
        verbose_name='Тип',
        help_text='Назначение голубя'
    )
    
    sex = models.CharField(
        max_length=20,
        choices=SEX_CHOICES,
        default='male',
        verbose_name='Пол',
        help_text='Пол голубя или пара'
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        help_text='Цена в сомони (TJS)'
    )
    
    description = models.TextField(
        verbose_name='Описание',
        help_text='Подробное описание птицы'
    )
    
    image = models.ImageField(
        upload_to='pigeons/',
        verbose_name='Фото',
        help_text='Основное фото голубя'
    )
    
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Видео (YouTube)',
        help_text='Ссылка на YouTube видео (необязательно)'
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
    
    city = models.CharField(
        max_length=50,
        choices=CITY_CHOICES,
        default='dushanbe',
        verbose_name='Город',
        help_text='Город продавца'
    )
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pigeons',
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
    
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Просмотры',
        help_text='Количество просмотров объявления'
    )
    
    favorites = models.ManyToManyField(
        User,
        related_name='favorite_pigeons',
        blank=True,
        verbose_name='В избранном у',
        help_text='Пользователи, добавившие в избранное'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    # Auction system fields
    listing_type = models.CharField(
        max_length=10,
        choices=LISTING_TYPE_CHOICES,
        default='fixed',
        verbose_name='Тип продажи'
    )
    
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
        related_name='won_auctions',
        verbose_name='Победитель аукциона'
    )
    
    # Payment verification fields for auctions
    payment_receipt = models.ImageField(
        upload_to='receipts/',
        blank=True,
        null=True,
        verbose_name='Чек оплаты',
        help_text='Скриншот чека оплаты для аукциона (3 TJS)'
    )
    
    is_paid = models.BooleanField(
        default=False,
        verbose_name='Оплачено',
        help_text='Оплата подтверждена администратором'
    )
    
    class Meta:
        verbose_name = 'Голубь'
        verbose_name_plural = 'Голуби'
        ordering = ['-is_vip', '-created_at']
        indexes = [
            models.Index(fields=['is_approved', '-created_at']),
            models.Index(fields=['breed', 'sex']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('pigeon_detail', kwargs={'pk': self.pk})
    
    def get_youtube_embed_url(self):
        """
        Convert YouTube URL to embed URL
        Supports formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        """
        if not self.video_url:
            return None
        
        video_id = None
        if 'youtube.com/watch?v=' in self.video_url:
            video_id = self.video_url.split('watch?v=')[-1].split('&')[0]
        elif 'youtu.be/' in self.video_url:
            video_id = self.video_url.split('youtu.be/')[-1].split('?')[0]
        
        if video_id:
            return f'https://www.youtube.com/embed/{video_id}'
        
        return None
    
    def is_auction_active(self):
        """Check if auction is currently active"""
        if self.listing_type != 'auction':
            return False
        if self.is_sold:
            return False
        if self.auction_end_date:
            from django.utils import timezone
            return timezone.now() < self.auction_end_date
        return False
    
    def get_highest_bid(self):
        """Get the highest bid for this pigeon"""
        return self.bids.first()
    
    def get_bid_count(self):
        """Get total number of bids"""
        return self.bids.count()


class Bid(models.Model):
    """Model for auction bids"""
    pigeon = models.ForeignKey(
        'Pigeon',
        on_delete=models.CASCADE,
        related_name='bids',
        verbose_name='Голубь'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='my_bids',
        verbose_name='Покупатель'
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
        ordering = ['-amount', '-created_at']
        verbose_name = 'Ставка'
        verbose_name_plural = 'Ставки'
        
    def __str__(self):
        return f"{self.user.username} - {self.amount} TJS на {self.pigeon.title}"


class Comment(models.Model):
    """Model for pigeon Q&A comments"""
    pigeon = models.ForeignKey(
        'Pigeon',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Голубь'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    
    text = models.TextField(
        verbose_name='Вопрос/Комментарий',
        help_text='Ваш вопрос о голубе'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        
    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}..."


class UserProfile(models.Model):
    """Extended user profile for additional fields"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Telegram Chat ID',
        help_text='ID для уведомлений в Telegram (получите у @userinfobot)'
    )
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"Profile of {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Review(models.Model):
    """
    User review/rating model for sellers
    """
    RATING_CHOICES = [
        (1, '⭐ 1 - Очень плохо'),
        (2, '⭐⭐ 2 - Плохо'),
        (3, '⭐⭐⭐ 3 - Нормально'),
        (4, '⭐⭐⭐⭐ 4 - Хорошо'),
        (5, '⭐⭐⭐⭐⭐ 5 - Отлично'),
    ]
    
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        verbose_name='Продавец'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wrote_reviews',
        verbose_name='Автор отзыва'
    )
    
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name='Оценка'
    )
    
    text = models.TextField(
        blank=True,
        verbose_name='Комментарий',
        help_text='Опишите ваш опыт покупки'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        # Constraint: One review per author-seller pair
        unique_together = ['seller', 'author']
        # Constraint: User cannot review themselves
        constraints = [
            models.CheckConstraint(
                check=~models.Q(seller=models.F('author')),
                name='no_self_review'
            )
        ]
    
    def __str__(self):
        return f"{self.author.username} → {self.seller.username}: {self.rating}⭐"
    
    def get_stars_display(self):
        """Return visual star representation"""
        filled = '⭐' * self.rating
        empty = '☆' * (5 - self.rating)
        return filled + empty


class PigeonImage(models.Model):
    """
    Model for storing multiple images for a single pigeon listing
    Supports up to 5 images per pigeon for better presentation
    """
    pigeon = models.ForeignKey(
        Pigeon,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Голубь'
    )
    
    image = models.ImageField(
        upload_to='pigeon_images/',
        verbose_name='Изображение'
    )
    
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Порядок',
        help_text='Порядок отображения изображения (0 = первое)'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )
    
    class Meta:
        verbose_name = 'Изображение голубя'
        verbose_name_plural = 'Изображения голубей'
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"{self.pigeon.title} - Image {self.order + 1}"


class HealthGuide(models.Model):
    """
    Model for Health Encyclopedia - guides for pigeon diseases and treatment
    """
    # Titles in both languages
    title_ru = models.CharField(
        max_length=255,
        verbose_name='Название (RU)'
    )
    
    title_tj = models.CharField(
        max_length=255,
        verbose_name='Название (TJ)'
    )
    
    # Descriptions
    description_ru = models.TextField(
        verbose_name='Описание (RU)',
        help_text='Краткое описание заболевания'
    )
    
    description_tj = models.TextField(
        verbose_name='Описание (TJ)',
        help_text='Краткое описание заболевания'
    )
    
    # Symptoms
    symptoms_ru = models.TextField(
        verbose_name='Симптомы (RU)',
        help_text='Описание симптомов заболевания'
    )
    
    symptoms_tj = models.TextField(
        verbose_name='Симптомы (TJ)',
        help_text='Описание симптомов заболевания'
    )
    
    # Treatment
    treatment_ru = models.TextField(
        verbose_name='Лечение (RU)',
        help_text='Методы и рекомендации по лечению'
    )
    
    treatment_tj = models.TextField(
        verbose_name='Лечение (TJ)',
        help_text='Методы и рекомендации по лечению'
    )
    
    # Image
    image = models.ImageField(
        upload_to='health_guides/',
        verbose_name='Изображение',
        help_text='Главное изображение для статьи'
    )
    
    # YouTube video (optional)
    youtube_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='YouTube видео',
        help_text='Ссылка на видео (например: https://www.youtube.com/watch?v=VIDEO_ID)'
    )
    
    # Slug for URLs
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='URL slug',
        help_text='Будет создан автоматически из названия'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Статья о здоровье'
        verbose_name_plural = 'Энциклопедия лечения'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title_ru
    
    def get_absolute_url(self):
        return reverse('health_detail', kwargs={'slug': self.slug})
    
    def get_youtube_embed_url(self):
        """
        Convert regular YouTube URL to embed URL for iframe
        Supports formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        """
        if not self.youtube_url:
            return None
        
        video_id = None
        
        # Handle youtube.com/watch?v= format
        if 'youtube.com/watch?v=' in self.youtube_url:
            video_id = self.youtube_url.split('watch?v=')[1].split('&')[0]
        # Handle youtu.be/ format
        elif 'youtu.be/' in self.youtube_url:
            video_id = self.youtube_url.split('youtu.be/')[1].split('?')[0]
        
        if video_id:
            return f'https://www.youtube.com/embed/{video_id}'
        
        return None

