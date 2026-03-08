"""
Admin configuration for ZooBozor with Django Unfold
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Animal, Bid, Comment, UserProfile, Review, AnimalImage, Veterinarian, Offer, Transaction
from django import forms
from decimal import Decimal


class TopUpForm(forms.Form):
    """Форма для пополнения баланса пользователя"""
    amount = forms.DecimalField(
        label='Сумма пополнения (TJS)',
        min_value=Decimal('0.01'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '100.00'
        })
    )
    description = forms.CharField(
        label='Описание (опционально)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Причина пополнения'
        })
    )


class AnimalImageInline(admin.TabularInline):
    """
    Inline admin for multiple animal images
    """
    model = AnimalImage
    extra = 1
    max_num = 5
    fields = ['image']
    readonly_fields = ['uploaded_at']


@admin.register(Animal)
class AnimalAdmin(ModelAdmin):
    """
    Admin interface for Animal model with Unfold
    """
    list_display = ['title', 'category_badge', 'price', 'owner', 'city', 'is_approved', 'is_vip', 'listing_type', 'is_paid', 'payment_receipt_preview', 'created_at']
    list_filter = ['is_approved', 'is_vip', 'listing_type', 'is_paid', 'is_sold', 'category', 'city', 'created_at']
    list_filter_submit = True  # Unfold feature: Submit button for filters
    search_fields = ['title', 'description', 'phone', 'owner__username', 'breed']
    list_editable = ['is_approved', 'is_vip', 'is_paid']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'payment_receipt_display']
    inlines = [AnimalImageInline]
    list_per_page = 25  # Pagination

    @display(description='📁 Категория', ordering='category')
    def category_badge(self, obj):
        """Show category with coloured emoji badge"""
        EMOJI = {
            'cat': '🐈', 'dog': '🐕', 'pigeon': '🕊️', 'parrot': '🦜',
            'horse': '🐎', 'cow': '🐄', 'sheep': '🐑', 'goat': '🐐',
            'rabbit': '🐇', 'fish': '🐠', 'transport': '🚖',
            'chicken': '🐔', 'canary': '🐦', 'hamster': '🐹',
            'turtle': '🐢', 'partridge': '🦅',
        }
        COLOR = {
            'transport': '#f59e0b', 'pigeon': '#10b981',
            'cat': '#8b5cf6', 'dog': '#6366f1',
            'cow': '#ef4444', 'sheep': '#ef4444', 'horse': '#ef4444', 'goat': '#ef4444',
        }
        emoji = EMOJI.get(obj.category, '🐾')
        color = COLOR.get(obj.category, '#D4AF37')
        label = obj.get_category_display().split('/')[0].strip()
        return format_html(
            '<span style="background:{}22;color:{};border:1px solid {}55;'
            'padding:2px 8px;border-radius:12px;font-size:12px;white-space:nowrap;">'
            '{} {}</span>',
            color, color, color, emoji, label
        )

    @display(description='🧾 Чек', ordering='payment_receipt')
    def payment_receipt_preview(self, obj):
        if obj.payment_receipt:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="object-fit: cover; border: 2px solid #D4AF37; border-radius: 4px;" /></a>',
                obj.payment_receipt.url,
                obj.payment_receipt.url
            )
        return '-'

    @display(description='🧾 Чек оплаты (Превью)')
    def payment_receipt_display(self, obj):
        """Display payment receipt as large image in detail view"""
        if obj.payment_receipt:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 500px; max-height: 500px; border: 3px solid #D4AF37; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);" /></a><br><br><a href="{}" target="_blank" style="color: #D4AF37; font-weight: bold; text-decoration: none;">🔗 Открыть в полном размере</a>',
                obj.payment_receipt.url,
                obj.payment_receipt.url,
                obj.payment_receipt.url
            )
        return format_html('<span style="color: #999;">Чек не загружен</span>')
    
    fieldsets = (
        ('📋 Основная информация', {
            'fields': ('title', 'category', 'description', 'city', 'price', 'is_negotiable')
        }),
        ('🐾 Характеристики животного', {
            'fields': ('breed', 'gender', 'age', 'weight', 'gender_livestock', 'color_variety', 'health_status', 'has_passport'),
            'classes': ('collapse',),
        }),
        ('🕊️ Поля для голубей', {
            'fields': ('flight_duration', 'game_style'),
            'classes': ('collapse',),
        }),
        ('🚖 Зоо-Такси (транспорт)', {
            'fields': ('transport_type', 'route_from', 'route_to', 'departure_time', 'available_days', 'cargo_capacity'),
            'classes': ('collapse',),
        }),
        ('💰 Тип продажи и аукцион', {
            'fields': ('listing_type', 'start_price', 'current_price', 'auction_end_date', 'is_sold', 'winner'),
        }),
        ('🧾 Оплата аукциона', {
            'fields': ('payment_receipt_display', 'is_paid'),
            'classes': ('collapse',),
        }),
        ('📞 Контакты', {
            'fields': ('phone', 'whatsapp_number', 'telegram_username')
        }),
        ('📸 Медиа', {
            'fields': ('main_photo', 'video_url')
        }),
        ('⭐ Владелец и статус', {
            'fields': ('owner', 'is_approved', 'is_vip')
        }),
        ('🕐 Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_animals', 'disapprove_animals', 'make_vip', 'approve_payment']
    
    @display(description='✅ Подтвердить оплату аукциона')
    def approve_payment(self, request, queryset):
        """Approve payment for auction listings"""
        updated = queryset.filter(listing_type='auction').update(is_paid=True)
        self.message_user(request, f'{updated} аукцион(ов) отмечено как оплачено')
    
    @display(description='✅ Одобрить выбранные объявления')
    def approve_animals(self, request, queryset):
        """Approve selected animals"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} объявлений одобрено.')
    
    @display(description='❌ Снять с публикации')
    def disapprove_animals(self, request, queryset):
        """Disapprove selected animals"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} объявлений снято с публикации.')
    
    @display(description='⭐ Сделать VIP')
    def make_vip(self, request, queryset):
        """Make selected animals VIP"""
        updated = queryset.update(is_vip=True)
        self.message_user(request, f'{updated} объявлений получили VIP статус.')


@admin.register(Bid)
class BidAdmin(ModelAdmin):
    """
    Admin interface for Bid model
    """
    list_display = ['animal', 'bidder', 'amount', 'created_at']
    list_filter = ['created_at', 'animal']
    search_fields = ['bidder__username', 'animal__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('animal', 'bidder')


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    """
    Admin interface for Comment model
    """
    list_display = ['author', 'animal', 'text_preview', 'created_at']
    list_filter = ['created_at', 'animal']
    list_filter_submit = True
    search_fields = ['author__username', 'animal__title', 'text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    @display(description='Текст')
    def text_preview(self, obj):
        """Show first 50 characters of text"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('animal', 'author')


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    """
    Admin interface for UserProfile model
    """
    list_display = ['user', 'balance_display', 'rating', 'total_sales', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'telegram_chat_id']
    readonly_fields = ['user', 'created_at', 'balance_display']
    list_filter = ['is_verified', 'created_at']
    list_filter_submit = True
    
    fieldsets = (
        ('Информация о пользователе', {
            'fields': ('user', 'phone', 'telegram_chat_id', 'created_at')
        }),
        ('Кошелек', {
            'fields': ('balance_display',),
            'description': 'Текущий баланс внутреннего кошелька'
        }),
        ('Статус продавца', {
            'fields': ('rating', 'total_sales', 'is_verified')
        }),
    )
    
    actions = ['top_up_balance']
    
    @display(description='💰 Баланс')
    def balance_display(self, obj):
        """Показать баланс с форматированием"""
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: #D4AF37;">{} TJS</span>',
            obj.balance
        )
    
    @display(description='💳 Пополнить баланс')
    def top_up_balance(self, request, queryset):
        """Экшен для пополнения баланса пользователя"""
        # Переносим в специальное представление для обработки
        selected_ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if len(selected_ids) != 1:
            self.message_user(request, '❌ Выберите ровно одного пользователя для пополнения баланса')
            return
        
        return HttpResponseRedirect(f'/admin/core/userprofile/{selected_ids[0]}/topup/')
    
    def get_urls(self):
        """Добавляем URL для пополнения баланса"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:profile_id>/topup/',
                self.admin_site.admin_view(self.topup_view),
                name='userprofile_topup',
            ),
        ]
        return custom_urls + urls
    
    def topup_view(self, request, profile_id):
        """Представление для пополнения баланса"""
        profile = UserProfile.objects.get(id=profile_id)
        
        if request.method == 'POST':
            form = TopUpForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                description = form.cleaned_data['description'] or 'Пополнение баланса администратором'
                
                try:
                    profile.add_balance(amount, description)
                    self.message_user(
                        request,
                        f'✅ Баланс пользователя {profile.user.username} пополнен на {amount} TJS. Новый баланс: {profile.balance} TJS'
                    )
                    return HttpResponseRedirect('/admin/core/userprofile/')
                except Exception as e:
                    self.message_user(request, f'❌ Ошибка: {str(e)}')
        else:
            form = TopUpForm()
        
        context = {
            'title': f'Пополнение баланса - {profile.user.username}',
            'form': form,
            'profile': profile,
            'opts': UserProfile._meta,
        }
        return render(request, 'admin/topup_form.html', context)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    """
    Admin interface for Transaction model (wallet history)
    """
    list_display = ['user', 'amount', 'transaction_type', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    list_filter_submit = True
    search_fields = ['user__username', 'user__email', 'description']
    readonly_fields = ['user', 'created_at']
    
    fieldsets = (
        ('Информация о транзакции', {
            'fields': ('user', 'amount', 'transaction_type', 'created_at')
        }),
        ('Описание', {
            'fields': ('description',)
        }),
    )
    
    def has_add_permission(self, request):
        """Не позволяем вручную создавать транзакции"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Не позволяем удалять историю транзакций"""
        return False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').order_by('-created_at')


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    """
    Admin interface for Review model
    """
    list_display = ['seller', 'buyer', 'rating', 'text_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    list_filter_submit = True
    search_fields = ['seller__username', 'buyer__username', 'text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Информация об отзыве', {
            'fields': ('seller', 'buyer', 'rating')
        }),
        ('Комментарий', {
            'fields': ('text',)
        }),
        ('Дата', {
            'fields': ('created_at',)
        }),
    )
    
    @display(description='Текст отзыва')
    def text_preview(self, obj):
        """Show first 60 characters of text"""
        if obj.text:
            return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
        return '(Без комментария)'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('seller', 'buyer')


@admin.register(Veterinarian)
class VeterinarianAdmin(ModelAdmin):
    """
    Admin interface for Veterinarian directory
    """
    list_display = ['name', 'city', 'phone', 'is_approved', 'is_vip', 'created_at']
    list_filter = ['city', 'is_approved', 'is_vip', 'created_at']
    search_fields = ['name', 'city', 'description', 'address']
    readonly_fields = ['created_at', 'updated_at', 'photo_display']
    list_editable = ['is_approved', 'is_vip']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'city', 'address')
        }),
        ('Описание услуг', {
            'fields': ('description',)
        }),
        ('Контакты', {
            'fields': ('phone', 'whatsapp_number')
        }),
        ('Медиа', {
            'fields': ('photo', 'photo_display')
        }),
        ('Статус', {
            'fields': ('is_approved', 'is_vip')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Фото')
    def photo_display(self, obj):
        """Display image in detail view"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 400px; border: 3px solid #D4AF37; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);" />',
                obj.photo.url
            )
        return 'Нет фото'
    
    actions = ['approve_veterinarians', 'make_vip']
    
    @display(description='✅ Одобрить')
    def approve_veterinarians(self, request, queryset):
        """Approve selected veterinarians"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} ветеринаров одобрено.')
    
    @display(description='⭐ Сделать VIP')
    def make_vip(self, request, queryset):
        """Make selected veterinarians VIP"""
        updated = queryset.update(is_vip=True)
        self.message_user(request, f'{updated} ветеринаров получили VIP статус.')


# Регистрация AnimalImage отдельно для управления
@admin.register(AnimalImage)
class AnimalImageAdmin(ModelAdmin):
    list_display = ['animal', 'image_preview', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['animal__title']
    ordering = ['animal', '-uploaded_at']
    
    @display(description='Превью')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'


@admin.register(Offer)
class OfferAdmin(ModelAdmin):
    """
    Admin interface for price offers
    """
    list_display = ['animal', 'buyer', 'price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    list_filter_submit = True
    search_fields = ['animal__title', 'buyer__username']
    readonly_fields = ['created_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Информация о предложении', {
            'fields': ('animal', 'buyer', 'price', 'status')
        }),
        ('Сообщение', {
            'fields': ('message',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['accept_offers', 'reject_offers']
    
    @display(description='✅ Принять предложения')
    def accept_offers(self, request, queryset):
        """Accept selected offers"""
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} предложений принято.')
    
    @display(description='❌ Отклонить предложения')
    def reject_offers(self, request, queryset):
        """Reject selected offers"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} предложений отклонено.')
