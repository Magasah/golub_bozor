"""
Models for GolubBozor - Pigeon Marketplace
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Pigeon(models.Model):
    """
    Model representing a pigeon listing on the marketplace
    """
    
    # Breed choices
    BREED_CHOICES = [
        ('lailaki', 'Лайлаки'),
        ('chinny', 'Чинни'),
        ('sochi', 'Сочи'),
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
