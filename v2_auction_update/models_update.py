# ДОБАВЬ ЭТО В core/models.py

from django.db import models
from django.contrib.auth.models import User

# Добавь это в начало файла, после импортов
LISTING_TYPE_CHOICES = [
    ('fixed', 'Фиксированная цена'),
    ('auction', 'Аукцион'),
]

# В модель Pigeon добавь эти новые поля (после существующих):
"""
class Pigeon(models.Model):
    # ... все существующие поля остаются ...
    
    # НОВЫЕ ПОЛЯ ДЛЯ АУКЦИОНА:
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
    
    def is_auction_active(self):
        if self.listing_type != 'auction':
            return False
        if self.is_sold:
            return False
        if self.auction_end_date:
            from django.utils import timezone
            return timezone.now() < self.auction_end_date
        return False
    
    def get_highest_bid(self):
        return self.bids.first()
    
    def get_bid_count(self):
        return self.bids.count()
"""


# НОВАЯ МОДЕЛЬ - добавь в конец файла core/models.py:
class Bid(models.Model):
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
