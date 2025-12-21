"""
Admin configuration for GolubBozor
"""
from django.contrib import admin
from .models import Pigeon


@admin.register(Pigeon)
class PigeonAdmin(admin.ModelAdmin):
    """
    Admin interface for Pigeon model
    """
    list_display = ['title', 'breed', 'sex', 'price', 'owner', 'is_approved', 'is_vip', 'created_at']
    list_filter = ['is_approved', 'is_vip', 'breed', 'sex', 'game_type', 'created_at']
    search_fields = ['title', 'description', 'phone', 'owner__username']
    list_editable = ['is_approved', 'is_vip']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'breed', 'game_type', 'sex', 'price', 'description')
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
    
    actions = ['approve_pigeons', 'disapprove_pigeons', 'make_vip']
    
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
