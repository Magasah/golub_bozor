"""
Admin configuration for GolubBozor
"""
from django.contrib import admin
from .models import Pigeon, Bid, Comment, UserProfile, Review, PigeonImage


class PigeonImageInline(admin.TabularInline):
    """
    Inline admin for multiple pigeon images
    """
    model = PigeonImage
    extra = 1
    max_num = 5
    fields = ['image', 'order']
    readonly_fields = ['uploaded_at']


@admin.register(Pigeon)
class PigeonAdmin(admin.ModelAdmin):
    """
    Admin interface for Pigeon model
    Supports multiple images via inline
    """
    list_display = ['title', 'breed', 'sex', 'price', 'owner', 'is_approved', 'is_vip', 'listing_type', 'is_paid', 'current_price', 'is_sold', 'created_at']
    list_filter = ['is_approved', 'is_vip', 'listing_type', 'is_paid', 'is_sold', 'breed', 'sex', 'game_type', 'created_at']
    search_fields = ['title', 'description', 'phone', 'owner__username']
    list_editable = ['is_approved', 'is_vip', 'is_paid']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PigeonImageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'breed', 'game_type', 'sex', 'price', 'description')
        }),
        ('Тип продажи', {
            'fields': ('listing_type', 'start_price', 'current_price')
        }),
        ('Аукцион', {
            'fields': ('auction_end_date', 'is_sold', 'winner'),
            'classes': ('collapse',),
        }),
        ('Оплата аукциона', {
            'fields': ('payment_receipt', 'is_paid'),
            'classes': ('collapse',),
        }),
        ('Контакты', {
            'fields': ('phone', 'whatsapp_number', 'telegram_username')
        }),
        ('Медиа', {
            'fields': ('image', 'video_url')
        }),
        ('Владелец и статус', {
            'fields': ('owner', 'is_approved', 'is_vip')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_pigeons', 'disapprove_pigeons', 'make_vip', 'approve_payment']
    
    def approve_payment(self, request, queryset):
        """Approve payment for auction listings"""
        updated = queryset.filter(listing_type='auction').update(is_paid=True)
        self.message_user(request, f'{updated} аукцион(ов) отмечено как оплачено')
    approve_payment.short_description = '✅ Подтвердить оплату аукциона'
    
    def approve_pigeons(self, request, queryset):
        """Approve selected pigeons"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} объявлений одобрено.')
    approve_pigeons.short_description = '✅ Одобрить выбранные объявления'
    
    def disapprove_pigeons(self, request, queryset):
        """Disapprove selected pigeons"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} объявлений снято с публикации.')
    disapprove_pigeons.short_description = '❌ Снять с публикации'
    
    def make_vip(self, request, queryset):
        """Make selected pigeons VIP"""
        updated = queryset.update(is_vip=True)
        self.message_user(request, f'{updated} объявлений получили VIP статус.')
    make_vip.short_description = '⭐ Сделать VIP'


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    """
    Admin interface for Bid model
    """
    list_display = ['pigeon', 'user', 'amount', 'created_at']
    list_filter = ['created_at', 'pigeon']
    search_fields = ['user__username', 'pigeon__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pigeon', 'user')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model
    """
    list_display = ['user', 'pigeon', 'text_preview', 'created_at']
    list_filter = ['created_at', 'pigeon']
    search_fields = ['user__username', 'pigeon__title', 'text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def text_preview(self, obj):
        """Show first 50 characters of text"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pigeon', 'user')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model
    """
    list_display = ['user', 'telegram_chat_id']
    search_fields = ['user__username', 'telegram_chat_id']
    readonly_fields = ['user']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin interface for Review model
    """
    list_display = ['seller', 'author', 'rating', 'text_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['seller__username', 'author__username', 'text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Информация об отзыве', {
            'fields': ('seller', 'author', 'rating')
        }),
        ('Комментарий', {
            'fields': ('text',)
        }),
        ('Дата', {
            'fields': ('created_at',)
        }),
    )
    
    def text_preview(self, obj):
        """Show first 60 characters of text"""
        if obj.text:
            return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
        return '(Без комментария)'
    text_preview.short_description = 'Текст отзыва'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('seller', 'author')
