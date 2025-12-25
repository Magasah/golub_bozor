# ДОБАВЬ ЭТО В core/admin.py

from django.contrib import admin
from .models import Pigeon, Bid

# Добавь в конец файла:

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['pigeon', 'user', 'amount', 'created_at']
    list_filter = ['created_at', 'pigeon']
    search_fields = ['user__username', 'pigeon__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pigeon', 'user')


# Также обнови существующий PigeonAdmin - добавь новые поля:
"""
@admin.register(Pigeon)
class PigeonAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'listing_type', 'price', 
        'current_price', 'is_sold', 'created_at'
    ]
    list_filter = ['listing_type', 'is_sold', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'user')
        }),
        ('Тип продажи', {
            'fields': ('listing_type', 'price', 'start_price', 'current_price')
        }),
        ('Аукцион', {
            'fields': ('auction_end_date', 'is_sold', 'winner'),
            'classes': ('collapse',),
        }),
        ('Дополнительно', {
            'fields': ('age', 'image1', 'image2', 'image3', 'created_at')
        }),
    )
"""
