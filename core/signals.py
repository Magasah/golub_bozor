"""
Django signals for GolubBozor
Auto-post new pigeons to Telegram Channel when created or approved
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Pigeon
from .utils import send_telegram_message
import logging

logger = logging.getLogger(__name__)

# Track original is_approved state
@receiver(pre_save, sender=Pigeon)
def track_approval_change(sender, instance, **kwargs):
    """Store original is_approved value before save"""
    if instance.pk:
        try:
            original = Pigeon.objects.get(pk=instance.pk)
            instance._original_is_approved = original.is_approved
        except Pigeon.DoesNotExist:
            instance._original_is_approved = False
    else:
        instance._original_is_approved = False


@receiver(post_save, sender=Pigeon)
def auto_post_to_channel(sender, instance, created, **kwargs):
    """
    Auto-post pigeon to Telegram Channel when:
    1. New pigeon is created (created=True)
    2. Pigeon is approved (is_approved changed from False to True)
    """
    try:
        # Check if pigeon should be posted
        should_post = False
        
        if created:
            # New pigeon created - post if approved
            should_post = instance.is_approved
            logger.info(f"New pigeon created: {instance.title}, is_approved={instance.is_approved}")
        else:
            # Check if approval status changed
            original_approved = getattr(instance, '_original_is_approved', False)
            if not original_approved and instance.is_approved:
                should_post = True
                logger.info(f"Pigeon approved: {instance.title}")
        
        if not should_post:
            logger.debug(f"Pigeon {instance.title} not posted: created={created}, approved={instance.is_approved}")
            return
        
        # Build absolute URL
        domain = getattr(settings, 'SITE_DOMAIN', 'http://127.0.0.1:8000')
        pigeon_url = f"{domain}{instance.get_absolute_url()}"
        
        # Format message with Markdown (for photos)
        if instance.listing_type == 'auction':
            message = (
                f"🦅 *НОВЫЙ АУКЦИОН!*\n\n"
                f"🕊️ *{instance.title}*\n"
                f"💰 Стартовая цена: *{instance.start_price} с.*\n"
                f"📍 Локация: {instance.location or 'Не указано'}\n"
                f"⏰ Окончание: {instance.auction_end_date.strftime('%d.%m.%Y %H:%M') if instance.auction_end_date else 'Не указано'}\n\n"
                f"👉 [Сделать ставку]({pigeon_url})"
            )
        else:
            message = (
                f"🦅 *НОВЫЙ ЛОТ!*\n\n"
                f"🕊️ *{instance.title}*\n"
                f"💰 Цена: *{instance.price} с.*\n"
                f"📍 Локация: {instance.location or 'Не указано'}\n\n"
                f"👉 [Купить сейчас]({pigeon_url})"
            )
        
        # Get image path
        image_path = None
        if instance.image and hasattr(instance.image, 'path'):
            image_path = instance.image.path
            logger.info(f"Image path: {image_path}")
        
        # Send to channel
        channel_username = "@GolubBozorChannel"
        success = send_telegram_message(
            chat_id=channel_username,
            text=message,
            image_path=image_path
        )
        
        if success:
            logger.info(f"Successfully posted pigeon '{instance.title}' to {channel_username}")
        else:
            logger.error(f"Failed to post pigeon '{instance.title}' to {channel_username}")
            
    except Exception as e:
        # Log error but don't prevent save operation
        logger.exception(f"Error in auto_post_to_channel for pigeon {instance.pk}: {str(e)}")
