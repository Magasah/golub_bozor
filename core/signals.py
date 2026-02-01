"""
Signals for ZooBozor - Telegram notifications with category-based emojis
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Animal, Bid, UserProfile
from .utils import send_telegram_message
from django.contrib.auth.models import User
import os


# Category emoji mapping
CATEGORY_EMOJIS = {
    'cat': '🐈',
    'dog': '🐕',
    'parrot': '🦜',
    'canary': '🐤',
    'partridge': '🦅',
    'chicken': '🐔',
    'pigeon': '🕊️',
    'rabbit': '🐰',
    'horse': '🐎',
    'cow': '🐄',
    'goat': '🐐',
    'sheep': '🐑',
    'fish': '🐠',
    'hamster': '🐹',
    'turtle': '🐢',
    'bird_other': '🦅',
    'reptile': '🦎',
    'other': '🦁',
}

CATEGORY_NAMES_RU = {
    'cat': 'КОШКА',
    'dog': 'СОБАКА',
    'parrot': 'ПОПУГАЙ',
    'canary': 'КАНАРЕЙКА',
    'partridge': 'КЕКЛИК',
    'chicken': 'КУРИЦА/ПЕТУХ',
    'pigeon': 'ГОЛУБЬ',
    'rabbit': 'КРОЛИК',
    'horse': 'ЛОШАДЬ',
    'cow': 'КОРОВА',
    'goat': 'КОЗА',
    'sheep': 'БАРАН',
    'fish': 'РЫБКА',
    'hamster': 'ХОМЯК',
    'turtle': 'ЧЕРЕПАХА',
    'bird_other': 'ПТИЦА',
    'reptile': 'РЕПТИЛИЯ',
    'other': 'ЖИВОТНОЕ',
}


@receiver(post_save, sender=Animal)
def notify_new_animal(sender, instance, created, **kwargs):
    """
    Send Telegram notification when a new animal listing is created
    """
    if created and instance.is_approved:
        # Get emoji and name for category
        emoji = CATEGORY_EMOJIS.get(instance.category, '🦁')
        animal_name = CATEGORY_NAMES_RU.get(instance.category, 'ЖИВОТНОЕ')
        
        # Build message
        message = f"{emoji} НОВОЕ ОБЪЯВЛЕНИЕ: {animal_name}!\n\n"
        message += f"📝 {instance.title}\n"
        message += f"💰 Цена: {instance.price} TJS\n"
        
        if instance.breed:
            message += f"🏷️ Порода: {instance.breed}\n"
        
        if instance.age:
            message += f"📅 Возраст: {instance.age}\n"
        
        message += f"📍 {instance.get_city_display()}\n"
        message += f"👤 Продавец: {instance.owner.username}\n"
        
        if instance.listing_type == 'auction':
            message += f"\n🔨 АУКЦИОН до {instance.auction_end_date.strftime('%d.%m.%Y %H:%M')}\n"
        
        # Add site link
        site_domain = os.environ.get('SITE_DOMAIN', 'http://127.0.0.1:8000')
        message += f"\n🔗 {site_domain}/animal/{instance.pk}/"
        
        # Send to channel/group
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        if chat_id:
            # Try to send with image if main_photo exists
            if instance.main_photo:
                try:
                    send_telegram_message(chat_id, message, image_path=instance.main_photo.path)
                except:
                    # If image fails, send text only
                    send_telegram_message(chat_id, message)
            else:
                send_telegram_message(chat_id, message)


@receiver(post_save, sender=Bid)
def notify_new_bid(sender, instance, created, **kwargs):
    """
    Notify seller about new bid on their pigeon auction
    """
    if created:
        animal = instance.animal
        seller = animal.owner
        
        # Check if seller has Telegram
        try:
            profile = seller.profile
            if profile.telegram_chat_id:
                emoji = CATEGORY_EMOJIS.get(animal.category, '🕊️')
                message = f"{emoji} НОВАЯ СТАВКА на ваш аукцион!\n\n"
                message += f"📝 {animal.title}\n"
                message += f"💰 Ставка: {instance.amount} TJS\n"
                message += f"👤 От: {instance.bidder.username}\n"
                message += f"⏰ {instance.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                
                site_domain = os.environ.get('SITE_DOMAIN', 'http://127.0.0.1:8000')
                message += f"\n🔗 {site_domain}/animal/{animal.pk}/"
                
                send_telegram_message(profile.telegram_chat_id, message)
        except:
            pass  # Profile doesn't exist or no telegram_chat_id


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when new User is created
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile when User is saved
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
