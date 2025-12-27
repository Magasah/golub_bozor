"""
Admin configuration for GolubBozor
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Pigeon, Bid, Comment, UserProfile, Review, PigeonImage, HealthGuide


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
    Shows payment receipt as image preview
    """
    list_display = ['title', 'breed', 'sex', 'price', 'owner', 'is_approved', 'is_vip', 'listing_type', 'is_paid', 'payment_receipt_preview', 'current_price', 'is_sold', 'created_at']
    list_filter = ['is_approved', 'is_vip', 'listing_type', 'is_paid', 'is_sold', 'breed', 'sex', 'game_type', 'created_at']
    search_fields = ['title', 'description', 'phone', 'owner__username']
    list_editable = ['is_approved', 'is_vip', 'is_paid']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'payment_receipt_display']
    inlines = [PigeonImageInline]
    
    def payment_receipt_preview(self, obj):
        """Display payment receipt as small thumbnail in list view"""
        if obj.payment_receipt:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="object-fit: cover; border: 2px solid #D4AF37; border-radius: 4px;" /></a>',
                obj.payment_receipt.url,
                obj.payment_receipt.url
            )
        return '-'
    payment_receipt_preview.short_description = '🧾 Чек'
    
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
    payment_receipt_display.short_description = '🧾 Чек оплаты (Превью)'
    
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
            'fields': ('payment_receipt_display', 'is_paid'),
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

@admin.register(HealthGuide)
class HealthGuideAdmin(admin.ModelAdmin):
    """
    Admin interface for Health Encyclopedia
    Automatically generates slug from Russian title
    """
    list_display = ['title_ru', 'title_tj', 'image_preview', 'has_video', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title_ru', 'title_tj', 'description_ru', 'description_tj']
    readonly_fields = ['slug', 'created_at', 'updated_at', 'image_display', 'video_preview']
    
    fieldsets = (
        ('🇷🇺 Контент (Русский)', {
            'fields': ('title_ru', 'description_ru', 'symptoms_ru', 'treatment_ru')
        }),
        ('🇹🇯 Контент (Таджикский)', {
            'fields': ('title_tj', 'description_tj', 'symptoms_tj', 'treatment_tj')
        }),
        ('📸 Медиа', {
            'fields': ('image', 'image_display', 'youtube_url', 'video_preview')
        }),
        ('⚙️ Технические данные', {
            'fields': ('slug', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Display thumbnail in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border: 2px solid #D4AF37; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = '🖼️'
    
    def image_display(self, obj):
        """Display large image in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 600px; border: 3px solid #D4AF37; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);" />',
                obj.image.url
            )
        return '-'
    image_display.short_description = 'Изображение (превью)'
    
    def has_video(self, obj):
        """Show if guide has YouTube video"""
        if obj.youtube_url:
            return format_html('<span style="color: green; font-weight: bold;">✓ Да</span>')
        return format_html('<span style="color: gray;">✗ Нет</span>')
    has_video.short_description = '🎥 Видео'
    
    def video_preview(self, obj):
        """Show YouTube video preview in admin"""
        embed_url = obj.get_youtube_embed_url()
        if embed_url:
            return format_html(
                '<iframe width="560" height="315" src="{}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="border: 3px solid #D4AF37; border-radius: 12px;"></iframe><br><br><a href="{}" target="_blank" style="color: #D4AF37; font-weight: bold;">🔗 Открыть на YouTube</a>',
                embed_url,
                obj.youtube_url
            )
        return '-'
    video_preview.short_description = 'Видео (превью)'
    
    def save_model(self, request, obj, form, change):
        """Auto-generate slug from Russian title if not set"""
        if not obj.slug:
            from django.utils.text import slugify
            from transliterate import translit
            
            # Transliterate Russian title to Latin for URL-friendly slug
            try:
                # Try to transliterate (requires transliterate package)
                base_slug = translit(obj.title_ru, 'ru', reversed=True)
            except:
                # Fallback to simple slugify if transliterate not available
                base_slug = obj.title_ru
            
            slug = slugify(base_slug)
            
            # Ensure unique slug
            counter = 1
            unique_slug = slug
            while HealthGuide.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{slug}-{counter}'
                counter += 1
            
            obj.slug = unique_slug
        
        super().save_model(request, obj, form, change)