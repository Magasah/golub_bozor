"""
Django management command to run the GolubBozor Telegram Bot
Premium Edition with Inline Keyboards & Markdown Formatting
"""
import telebot
from telebot import types
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from core.models import Pigeon, UserProfile, Bid
from core.utils import TELEGRAM_BOT_TOKEN


class Command(BaseCommand):
    help = 'Run the GolubBozor Telegram Bot (Premium Edition)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🦅 Starting GolubBozor Premium Bot...'))
        
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        
        # ==================== SET BOT COMMANDS ====================
        commands = [
            types.BotCommand('start', '🔄 Перезапуск / Главное меню'),
            types.BotCommand('profile', '👤 Мой кабинет'),
            types.BotCommand('my_pigeons', '🦅 Мои голуби'),
            types.BotCommand('admin', '🛡️ Панель управления (для админов)'),
            types.BotCommand('help', '🆘 Помощь'),
        ]
        try:
            bot.set_my_commands(commands)
            self.stdout.write(self.style.SUCCESS('✅ Bot commands configured'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Could not set commands: {str(e)}'))
        
        # ==================== HELPER FUNCTIONS ====================
        
        def get_user_from_telegram(chat_id):
            """Fetch UserProfile from Telegram chat_id"""
            try:
                profile = UserProfile.objects.filter(telegram_chat_id=str(chat_id)).first()
                return profile
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error fetching user: {str(e)}'))
                return None
        
        def get_main_menu_keyboard():
            """Create premium inline keyboard for main menu"""
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_profile = types.InlineKeyboardButton('👤 Кабинет Трейдера', callback_data='profile')
            btn_pigeons = types.InlineKeyboardButton('🦅 Мои Активы', callback_data='my_pigeons')
            btn_balance = types.InlineKeyboardButton('💰 Финансы', callback_data='balance')
            # WebApp Button - opens website inside Telegram
            btn_webapp = types.InlineKeyboardButton(
                '📱 Открыть Приложение',
                web_app=types.WebAppInfo(url='https://magaj.pythonanywhere.com')
            )
            markup.add(btn_profile, btn_pigeons)
            markup.add(btn_balance, btn_webapp)
            return markup
        
        def get_back_button():
            """Create back button keyboard"""
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🔙 В Главное Меню', callback_data='back_to_main'))
            return markup
        
        def get_welcome_text(profile=None):
            """Generate welcome text"""
            welcome = (
                "🦅 *Добро пожаловать в GolubBozor!*\n\n"
                "Главная биржа голубей Таджикистана.\n"
                "Управляйте бизнесом прямо отсюда."
            )
            if profile:
                welcome += f"\n\nПривет, *{profile.user.username}*! 💎"
            return welcome
        
        # ==================== COMMAND HANDLERS ====================
        
        @bot.message_handler(commands=['start'])
        def start_handler(message):
            """Handle /start command - Premium welcome screen"""
            try:
                chat_id = str(message.chat.id)
                profile = get_user_from_telegram(chat_id)
                
                # CRITICAL: Remove old reply keyboard buttons
                bot.send_message(
                    message.chat.id,
                    "🔄 Обновление интерфейса...",
                    reply_markup=types.ReplyKeyboardRemove()
                )
                
                if profile:
                    bot.send_message(
                        message.chat.id,
                        get_welcome_text(profile),
                        parse_mode='Markdown',
                        reply_markup=get_main_menu_keyboard()
                    )
                else:
                    welcome_text = (
                        "🦅 *Добро пожаловать в GolubBozor!*\n\n"
                        "Главная биржа голубей Таджикистана.\n"
                        "Управляйте бизнесом прямо отсюда.\n\n"
                        "⚠️ *Аккаунт не привязан*\n\n"
                        "Для подключения введите:\n"
                        "`/connect ваш_email@example.com`\n\n"
                        "Используйте email с которым вы зарегистрированы на сайте."
                    )
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('📖 Как привязать?', callback_data='help_connect'))
                    bot.send_message(
                        message.chat.id,
                        welcome_text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error in /start: {str(e)}'))
                bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте позже.")
        
        @bot.message_handler(commands=['profile'])
        def profile_command_handler(message):
            """Handle /profile command"""
            chat_id = str(message.chat.id)
            profile = get_user_from_telegram(chat_id)
            
            if not profile:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Сначала привяжите аккаунт через `/connect`",
                    parse_mode='Markdown'
                )
                return
            
            # Generate profile info
            user = profile.user
            count_total = Pigeon.objects.filter(owner=user).count()
            count_active = Pigeon.objects.filter(owner=user, is_approved=True, is_sold=False).count()
            count_auctions = Pigeon.objects.filter(owner=user, listing_type='auction', is_approved=True, is_sold=False).count()
            count_vip = Pigeon.objects.filter(owner=user, is_vip=True).count()
            
            profile_text = (
                "👤 *ЛИЧНОЕ ДЕЛО*\n\n"
                f"🆔 ID: `{user.id}`\n"
                f"👤 Логин: @{user.username}\n"
                f"📧 Email: `{user.email}`\n\n"
                "📊 *СТАТИСТИКА АКТИВНОСТИ*\n\n"
                f"🦅 Голубей в продаже: `{count_active}`\n"
                f"⏳ Аукционов идет: `{count_auctions}`\n"
                f"💎 VIP размещений: `{count_vip}`\n"
                f"📦 Всего объявлений: `{count_total}`"
            )
            
            bot.send_message(
                message.chat.id,
                profile_text,
                parse_mode='Markdown',
                reply_markup=get_back_button()
            )
        
        @bot.message_handler(commands=['my_pigeons'])
        def my_pigeons_command_handler(message):
            """Handle /my_pigeons command"""
            chat_id = str(message.chat.id)
            profile = get_user_from_telegram(chat_id)
            
            if not profile:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Сначала привяжите аккаунт через `/connect`",
                    parse_mode='Markdown'
                )
                return
            
            pigeons = Pigeon.objects.filter(owner=profile.user, is_approved=True)[:5]
            
            if not pigeons:
                pigeons_text = (
                    "🕊️ *У вас пока нет активных объявлений*\n\n"
                    "Создайте объявление на сайте!\n"
                    "[Добавить объявление](https://magaj.pythonanywhere.com/add_pigeon/)"
                )
            else:
                pigeons_text = "🦅 *МОИ АКТИВЫ (последние 5)*\n\n"
                for idx, pigeon in enumerate(pigeons, 1):
                    vip_badge = "💎 " if pigeon.is_vip else ""
                    listing_type = "🔨 Аукцион" if pigeon.listing_type == 'auction' else "💰 Продажа"
                    
                    if pigeon.listing_type == 'auction':
                        price = f"`{pigeon.current_price} TJS`"
                    else:
                        price = f"`{pigeon.price} TJS`"
                    
                    status = "✅ Активно" if not pigeon.is_sold else "❌ Продано"
                    
                    pigeons_text += (
                        f"{idx}. {vip_badge}*{pigeon.title}*\n"
                        f"   {listing_type} • {price}\n"
                        f"   {status} • 👁 `{pigeon.views_count}` просм.\n\n"
                    )
            
            bot.send_message(
                message.chat.id,
                pigeons_text,
                parse_mode='Markdown',
                reply_markup=get_back_button(),
                disable_web_page_preview=True
            )
        
        @bot.message_handler(commands=['help'])
        def help_command_handler(message):
            """Handle /help command"""
            help_text = (
                "🆘 *СПРАВКА И ПОДДЕРЖКА*\n\n"
                "*Доступные команды:*\n"
                "/start - Главное меню\n"
                "/profile - Мой кабинет\n"
                "/my_pigeons - Мои голуби\n"
                "/connect email - Привязать аккаунт\n\n"
                "*Контакты администрации:*\n"
                "📞 WhatsApp: +992 888 788 181\n"
                "🌐 Сайт: [magaj.pythonanywhere.com](https://magaj.pythonanywhere.com)\n\n"
                "💬 По всем вопросам пишите в WhatsApp!"
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🔙 В Главное Меню', callback_data='back_to_main'))
            
            bot.send_message(
                message.chat.id,
                help_text,
                parse_mode='Markdown',
                reply_markup=markup,
                disable_web_page_preview=True
            )
        
        @bot.message_handler(commands=['connect'])
        def connect_handler(message):
            """Handle /connect command - Link Telegram to Django account"""
            try:
                parts = message.text.split(maxsplit=1)
                if len(parts) < 2:
                    bot.send_message(
                        message.chat.id,
                        "❌ *Неверный формат команды!*\n\n"
                        "Используйте:\n"
                        "`/connect ваш_email@example.com`",
                        parse_mode='Markdown'
                    )
                    return
                
                email = parts[1].strip()
                chat_id = str(message.chat.id)
                
                # Find user by email
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    bot.send_message(
                        message.chat.id,
                        f"❌ *Пользователь с email `{email}` не найден!*\n\n"
                        "Проверьте правильность email или зарегистрируйтесь на сайте:\n"
                        "[magaj.pythonanywhere.com](https://magaj.pythonanywhere.com/register/)",
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    return
                
                # Get or create user profile and update telegram_chat_id
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.telegram_chat_id = chat_id
                profile.save()
                
                success_text = (
                    f"✅ *Аккаунт `{email}` успешно привязан!*\n\n"
                    "Теперь вы будете получать уведомления о:\n"
                    "• 💬 Новых вопросах к вашим объявлениям\n"
                    "• 💰 Новых ставках на аукционах\n"
                    "• ⚠️ Когда вас перебивают\n\n"
                    "Добро пожаловать в систему! 🦅"
                )
                bot.send_message(
                    message.chat.id,
                    success_text,
                    parse_mode='Markdown',
                    reply_markup=get_main_menu_keyboard()
                )
                
                self.stdout.write(self.style.SUCCESS(f'✅ User {user.username} connected: {chat_id}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error in /connect: {str(e)}'))
                bot.send_message(message.chat.id, "❌ Произошла ошибка при подключении.")
        
        @bot.message_handler(commands=['admin'])
        def admin_command_handler(message):
            """Handle /admin command - Admin Control Panel"""
            chat_id = str(message.chat.id)
            profile = get_user_from_telegram(chat_id)
            
            if not profile:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Сначала привяжите аккаунт через `/connect`",
                    parse_mode='Markdown'
                )
                return
            
            user = profile.user
            
            # Check if user is staff or superuser
            if not user.is_staff:
                bot.send_message(
                    message.chat.id,
                    "🚫 *Доступ запрещён*\n\n"
                    "Эта команда доступна только администраторам и модераторам.",
                    parse_mode='Markdown'
                )
                return
            
            # Get statistics for admin panel
            total_users = User.objects.count()
            total_pigeons = Pigeon.objects.count()
            pending_approval = Pigeon.objects.filter(is_approved=False).count()
            pending_payments = Pigeon.objects.filter(
                listing_type='auction',
                is_paid=False,
                payment_receipt__isnull=False
            ).exclude(payment_receipt='').count()
            active_auctions = Pigeon.objects.filter(
                listing_type='auction',
                is_approved=True,
                is_sold=False,
                auction_end_date__gt=timezone.now()
            ).count()
            
            # Create admin panel text
            role = "👑 СУПЕРАДМИНИСТРАТОР" if user.is_superuser else "🛡️ МОДЕРАТОР"
            
            admin_text = (
                f"{role}\n\n"
                f"🆔 ID: `{user.id}`\n"
                f"👤 Логин: @{user.username}\n\n"
                "📊 *СТАТИСТИКА ПЛАТФОРМЫ*\n\n"
                f"👥 Всего пользователей: `{total_users}`\n"
                f"🦅 Всего объявлений: `{total_pigeons}`\n"
                f"🔨 Активных аукционов: `{active_auctions}`\n"
                f"⏳ Ожидают одобрения: `{pending_approval}`\n"
                f"💳 Ожидают оплаты: `{pending_payments}`\n\n"
                "🔧 *ПАНЕЛЬ УПРАВЛЕНИЯ*"
            )
            
            # Create admin keyboard
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            # Common buttons for all staff
            btn_pending = types.InlineKeyboardButton(
                f'⏳ Одобрить объявления ({pending_approval})',
                callback_data='admin_pending'
            )
            btn_payments = types.InlineKeyboardButton(
                f'💳 Проверить оплаты ({pending_payments})',
                callback_data='admin_payments'
            )
            btn_stats = types.InlineKeyboardButton(
                '📊 Подробная статистика',
                callback_data='admin_stats'
            )
            btn_dashboard = types.InlineKeyboardButton(
                '🌐 Открыть Dashboard',
                web_app=types.WebAppInfo(url='https://magaj.pythonanywhere.com/dashboard/')
            )
            
            markup.add(btn_pending, btn_payments)
            markup.add(btn_stats, btn_dashboard)
            
            # Superuser exclusive buttons
            if user.is_superuser:
                btn_users = types.InlineKeyboardButton(
                    '👥 Управление пользователями',
                    callback_data='admin_users'
                )
                btn_broadcast = types.InlineKeyboardButton(
                    '📢 Рассылка сообщений',
                    callback_data='admin_broadcast'
                )
                markup.add(btn_users, btn_broadcast)
            
            btn_back = types.InlineKeyboardButton('🔙 Главное меню', callback_data='back_to_main')
            markup.add(btn_back)
            
            bot.send_message(
                message.chat.id,
                admin_text,
                parse_mode='Markdown',
                reply_markup=markup
            )
        
        # ==================== CALLBACK QUERY HANDLERS ====================
        
        @bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call):
            """Handle all inline button callbacks"""
            try:
                chat_id = call.message.chat.id
                message_id = call.message.message_id
                profile = get_user_from_telegram(chat_id)
                
                # Check authentication for protected actions
                protected_actions = ['profile', 'my_pigeons', 'balance']
                if call.data in protected_actions and not profile:
                    bot.answer_callback_query(
                        call.id,
                        "⚠️ Сначала привяжите аккаунт через /connect",
                        show_alert=True
                    )
                    return
                
                # ===== BACK TO MAIN =====
                if call.data == 'back_to_main':
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=get_welcome_text(profile),
                        parse_mode='Markdown',
                        reply_markup=get_main_menu_keyboard()
                    )
                    bot.answer_callback_query(call.id)
                
                # ===== PROFILE =====
                elif call.data == 'profile':
                    user = profile.user
                    count_total = Pigeon.objects.filter(owner=user).count()
                    count_active = Pigeon.objects.filter(owner=user, is_approved=True, is_sold=False).count()
                    count_auctions = Pigeon.objects.filter(owner=user, listing_type='auction', is_approved=True, is_sold=False).count()
                    count_vip = Pigeon.objects.filter(owner=user, is_vip=True).count()
                    count_sold = Pigeon.objects.filter(owner=user, is_sold=True).count()
                    
                    profile_text = (
                        "👤 *ЛИЧНОЕ ДЕЛО*\n\n"
                        f"🆔 ID: `{user.id}`\n"
                        f"👤 Логин: @{user.username}\n"
                        f"📧 Email: `{user.email}`\n\n"
                        "📊 *СТАТИСТИКА АКТИВНОСТИ*\n\n"
                        f"🦅 Голубей в продаже: `{count_active}`\n"
                        f"⏳ Аукционов идет: `{count_auctions}`\n"
                        f"💎 VIP размещений: `{count_vip}`\n"
                        f"✅ Продано: `{count_sold}`\n"
                        f"📦 Всего объявлений: `{count_total}`"
                    )
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=profile_text,
                        parse_mode='Markdown',
                        reply_markup=get_back_button()
                    )
                    bot.answer_callback_query(call.id, "✅ Личное дело загружено")
                
                # ===== MY PIGEONS =====
                elif call.data == 'my_pigeons':
                    pigeons = Pigeon.objects.filter(owner=profile.user, is_approved=True)[:5]
                    
                    if not pigeons:
                        pigeons_text = (
                            "🕊️ *У вас пока нет активных объявлений*\n\n"
                            "Создайте объявление на сайте!\n"
                            "[Добавить объявление](https://magaj.pythonanywhere.com/add_pigeon/)"
                        )
                    else:
                        pigeons_text = "🦅 *МОИ АКТИВЫ (последние 5)*\n\n"
                        for idx, pigeon in enumerate(pigeons, 1):
                            vip_badge = "💎 " if pigeon.is_vip else ""
                            listing_type = "🔨 Аукцион" if pigeon.listing_type == 'auction' else "💰 Продажа"
                            
                            if pigeon.listing_type == 'auction':
                                price = f"`{pigeon.current_price} TJS`"
                            else:
                                price = f"`{pigeon.price} TJS`"
                            
                            status = "✅ Активно" if not pigeon.is_sold else "❌ Продано"
                            
                            pigeons_text += (
                                f"{idx}. {vip_badge}*{pigeon.title}*\n"
                                f"   {listing_type} • {price}\n"
                                f"   {status} • 👁 `{pigeon.views_count}` просм.\n\n"
                            )
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=pigeons_text,
                        parse_mode='Markdown',
                        reply_markup=get_back_button(),
                        disable_web_page_preview=True
                    )
                    bot.answer_callback_query(call.id, "✅ Активы загружены")
                
                # ===== BALANCE =====
                elif call.data == 'balance':
                    user = profile.user
                    total_sales = Pigeon.objects.filter(owner=user, is_sold=True).count()
                    
                    balance_text = (
                        "💰 *ФИНАНСЫ*\n\n"
                        f"Текущий баланс: `0 TJS`\n"
                        f"Продано объявлений: `{total_sales}`\n\n"
                        "🔜 Функция пополнения баланса находится в разработке.\n\n"
                        "Для VIP размещения используйте форму на сайте."
                    )
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=balance_text,
                        parse_mode='Markdown',
                        reply_markup=get_back_button()
                    )
                    bot.answer_callback_query(call.id, "💰 Финансы")
                
                # ===== HELP CONNECT =====
                elif call.data == 'help_connect':
                    help_text = (
                        "📖 *КАК ПРИВЯЗАТЬ АККАУНТ*\n\n"
                        "1️⃣ Зарегистрируйтесь на сайте:\n"
                        "   [magaj.pythonanywhere.com](https://magaj.pythonanywhere.com/register/)\n\n"
                        "2️⃣ Введите команду:\n"
                        "   `/connect ваш_email@example.com`\n\n"
                        "3️⃣ Используйте email с которым регистрировались\n\n"
                        "✅ После привязки вы получите доступ ко всем функциям бота!"
                    )
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=help_text,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    bot.answer_callback_query(call.id)
                
                # ===== ADMIN PANEL CALLBACKS =====
                elif call.data == 'admin_pending':
                    pending = Pigeon.objects.filter(is_approved=False).order_by('-created_at')[:5]
                    
                    if not pending:
                        text = "✅ *Нет объявлений ожидающих одобрения*"
                    else:
                        text = "⏳ *ОЖИДАЮТ ОДОБРЕНИЯ*\n\n"
                        for idx, pigeon in enumerate(pending, 1):
                            text += (
                                f"{idx}. *{pigeon.title}*\n"
                                f"   Владелец: @{pigeon.owner.username}\n"
                                f"   Цена: `{pigeon.price} TJS`\n"
                                f"   Дата: {pigeon.created_at.strftime('%d.%m.%Y')}\n\n"
                            )
                        text += "\n🌐 [Открыть Django Admin для одобрения](https://magaj.pythonanywhere.com/control_panel_secret_7828/core/pigeon/)"
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('🔙 Назад в админку', callback_data='admin_back'))
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=text,
                        parse_mode='Markdown',
                        reply_markup=markup,
                        disable_web_page_preview=True
                    )
                    bot.answer_callback_query(call.id)
                
                elif call.data == 'admin_payments':
                    pending_payments = Pigeon.objects.filter(
                        listing_type='auction',
                        is_paid=False,
                        payment_receipt__isnull=False
                    ).exclude(payment_receipt='').order_by('-created_at')[:5]
                    
                    if not pending_payments:
                        text = "✅ *Нет ожидающих оплат*"
                    else:
                        text = "💳 *ОЖИДАЮТ ПРОВЕРКИ ОПЛАТЫ*\n\n"
                        for idx, pigeon in enumerate(pending_payments, 1):
                            text += (
                                f"{idx}. *{pigeon.title}*\n"
                                f"   Владелец: @{pigeon.owner.username}\n"
                                f"   Сумма: `3 TJS`\n\n"
                            )
                        text += "\n🌐 [Открыть Manager Dashboard](https://magaj.pythonanywhere.com/manager/dashboard/)"
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('🔙 Назад в админку', callback_data='admin_back'))
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=text,
                        parse_mode='Markdown',
                        reply_markup=markup,
                        disable_web_page_preview=True
                    )
                    bot.answer_callback_query(call.id)
                
                elif call.data == 'admin_stats':
                    total_users = User.objects.count()
                    total_pigeons = Pigeon.objects.count()
                    approved = Pigeon.objects.filter(is_approved=True).count()
                    pending = Pigeon.objects.filter(is_approved=False).count()
                    vip = Pigeon.objects.filter(is_vip=True).count()
                    sold = Pigeon.objects.filter(is_sold=True).count()
                    active_auctions = Pigeon.objects.filter(
                        listing_type='auction',
                        is_approved=True,
                        is_sold=False,
                        auction_end_date__gt=timezone.now()
                    ).count()
                    
                    text = (
                        "📊 *ПОДРОБНАЯ СТАТИСТИКА*\n\n"
                        "*Пользователи:*\n"
                        f"👥 Всего: `{total_users}`\n\n"
                        "*Объявления:*\n"
                        f"🦅 Всего: `{total_pigeons}`\n"
                        f"✅ Одобренных: `{approved}`\n"
                        f"⏳ Ожидают: `{pending}`\n"
                        f"💎 VIP: `{vip}`\n"
                        f"🎯 Продано: `{sold}`\n\n"
                        "*Аукционы:*\n"
                        f"🔨 Активных: `{active_auctions}`\n\n"
                        "🌐 [Открыть полный Dashboard](https://magaj.pythonanywhere.com/dashboard/)"
                    )
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('🔙 Назад в админку', callback_data='admin_back'))
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=text,
                        parse_mode='Markdown',
                        reply_markup=markup,
                        disable_web_page_preview=True
                    )
                    bot.answer_callback_query(call.id)
                
                elif call.data == 'admin_users':
                    # Superuser only
                    if not profile.user.is_superuser:
                        bot.answer_callback_query(call.id, "🚫 Только для суперадминов", show_alert=True)
                        return
                    
                    recent_users = User.objects.order_by('-date_joined')[:5]
                    staff_count = User.objects.filter(is_staff=True).count()
                    
                    text = (
                        "👥 *УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ*\n\n"
                        f"Всего пользователей: `{User.objects.count()}`\n"
                        f"Администраторов: `{staff_count}`\n\n"
                        "*Последние 5 регистраций:*\n\n"
                    )
                    
                    for idx, user in enumerate(recent_users, 1):
                        role = "👑" if user.is_superuser else "🛡️" if user.is_staff else "👤"
                        text += (
                            f"{idx}. {role} @{user.username}\n"
                            f"   Email: `{user.email}`\n"
                            f"   Дата: {user.date_joined.strftime('%d.%m.%Y')}\n\n"
                        )
                    
                    text += "\n🌐 [Открыть Django Admin](https://magaj.pythonanywhere.com/control_panel_secret_7828/auth/user/)"
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('🔙 Назад в админку', callback_data='admin_back'))
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=text,
                        parse_mode='Markdown',
                        reply_markup=markup,
                        disable_web_page_preview=True
                    )
                    bot.answer_callback_query(call.id)
                
                elif call.data == 'admin_broadcast':
                    # Superuser only
                    if not profile.user.is_superuser:
                        bot.answer_callback_query(call.id, "🚫 Только для суперадминов", show_alert=True)
                        return
                    
                    text = (
                        "📢 *РАССЫЛКА СООБЩЕНИЙ*\n\n"
                        "⚠️ Функция находится в разработке.\n\n"
                        "В будущем здесь можно будет:\n"
                        "• Отправлять сообщения всем пользователям\n"
                        "• Создавать таргетированные рассылки\n"
                        "• Просматривать статистику доставки\n\n"
                        "Пока используйте Telegram Channel для анонсов."
                    )
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('📢 Открыть Channel', url='https://t.me/GolubBozorChannel'))
                    markup.add(types.InlineKeyboardButton('🔙 Назад в админку', callback_data='admin_back'))
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                    bot.answer_callback_query(call.id)
                
                elif call.data == 'admin_back':
                    # Return to admin panel
                    # Re-call admin command logic
                    user = profile.user
                    total_users = User.objects.count()
                    total_pigeons = Pigeon.objects.count()
                    pending_approval = Pigeon.objects.filter(is_approved=False).count()
                    pending_payments = Pigeon.objects.filter(
                        listing_type='auction',
                        is_paid=False,
                        payment_receipt__isnull=False
                    ).exclude(payment_receipt='').count()
                    active_auctions = Pigeon.objects.filter(
                        listing_type='auction',
                        is_approved=True,
                        is_sold=False,
                        auction_end_date__gt=timezone.now()
                    ).count()
                    
                    role = "👑 СУПЕРАДМИНИСТРАТОР" if user.is_superuser else "🛡️ МОДЕРАТОР"
                    
                    admin_text = (
                        f"{role}\n\n"
                        f"🆔 ID: `{user.id}`\n"
                        f"👤 Логин: @{user.username}\n\n"
                        "📊 *СТАТИСТИКА ПЛАТФОРМЫ*\n\n"
                        f"👥 Всего пользователей: `{total_users}`\n"
                        f"🦅 Всего объявлений: `{total_pigeons}`\n"
                        f"🔨 Активных аукционов: `{active_auctions}`\n"
                        f"⏳ Ожидают одобрения: `{pending_approval}`\n"
                        f"💳 Ожидают оплаты: `{pending_payments}`\n\n"
                        "🔧 *ПАНЕЛЬ УПРАВЛЕНИЯ*"
                    )
                    
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    
                    btn_pending = types.InlineKeyboardButton(
                        f'⏳ Одобрить объявления ({pending_approval})',
                        callback_data='admin_pending'
                    )
                    btn_payments = types.InlineKeyboardButton(
                        f'💳 Проверить оплаты ({pending_payments})',
                        callback_data='admin_payments'
                    )
                    btn_stats = types.InlineKeyboardButton(
                        '📊 Подробная статистика',
                        callback_data='admin_stats'
                    )
                    btn_dashboard = types.InlineKeyboardButton(
                        '🌐 Открыть Dashboard',
                        web_app=types.WebAppInfo(url='https://magaj.pythonanywhere.com/dashboard/')
                    )
                    
                    markup.add(btn_pending, btn_payments)
                    markup.add(btn_stats, btn_dashboard)
                    
                    if user.is_superuser:
                        btn_users = types.InlineKeyboardButton(
                            '👥 Управление пользователями',
                            callback_data='admin_users'
                        )
                        btn_broadcast = types.InlineKeyboardButton(
                            '📢 Рассылка сообщений',
                            callback_data='admin_broadcast'
                        )
                        markup.add(btn_users, btn_broadcast)
                    
                    btn_back = types.InlineKeyboardButton('🔙 Главное меню', callback_data='back_to_main')
                    markup.add(btn_back)
                    
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=admin_text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                    bot.answer_callback_query(call.id)
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Callback error: {str(e)}'))
                bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
        
        # ==================== SEARCH HANDLER ====================
        
        @bot.message_handler(func=lambda message: not message.text.startswith('/'))
        def search_handler(message):
            """Handle text search for pigeons"""
            try:
                search_query = message.text.strip()
                
                if not search_query:
                    return
                
                # Search in Pigeon model
                results = Pigeon.objects.filter(
                    models.Q(title__icontains=search_query) | models.Q(description__icontains=search_query),
                    is_approved=True,
                    is_sold=False
                ).order_by('-created_at')[:3]
                
                if results:
                    response = f"🦅 *Найдено по запросу '{search_query}':*\n\n"
                    
                    for idx, pigeon in enumerate(results, 1):
                        if pigeon.listing_type == 'auction':
                            price = f"{pigeon.current_price} TJS"
                        else:
                            price = f"{pigeon.price} TJS"
                        
                        response += (
                            f"{idx}. *{pigeon.title}*\n"
                            f"   💰 {price}\n"
                            f"   🔗 /view\\_{pigeon.id}\n\n"
                        )
                    
                    response += "💡 _Нажмите /view\\_ID для подробностей_"
                    
                    bot.send_message(
                        message.chat.id,
                        response,
                        parse_mode='Markdown'
                    )
                else:
                    bot.send_message(
                        message.chat.id,
                        f"🦅 По запросу '*{search_query}*' ничего не найдено.\n\n"
                        "Попробуйте другое название или просмотрите каталог на сайте.",
                        parse_mode='Markdown'
                    )
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Search error: {str(e)}'))
                bot.send_message(message.chat.id, "❌ Ошибка поиска. Попробуйте позже.")
        
        # ==================== VIEW DETAILS HANDLER ====================
        
        @bot.message_handler(commands=['view'])
        def view_command_handler(message):
            """Handle /view_<id> command - Show pigeon details"""
            try:
                # Extract ID from command (format: /view_123)
                command = message.text.split('_')
                if len(command) < 2:
                    bot.send_message(
                        message.chat.id,
                        "❌ Неверный формат команды!\n\n"
                        "Используйте: `/view_ID`\n"
                        "Например: `/view_1`",
                        parse_mode='Markdown'
                    )
                    return
                
                pigeon_id = int(command[1])
                pigeon = Pigeon.objects.filter(id=pigeon_id, is_approved=True).first()
                
                if not pigeon:
                    bot.send_message(
                        message.chat.id,
                        "❌ Голубь не найден или снят с публикации.",
                        parse_mode='Markdown'
                    )
                    return
                
                # Format details
                vip_badge = "💎 VIP " if pigeon.is_vip else ""
                listing_type = "🔨 АУКЦИОН" if pigeon.listing_type == 'auction' else "💰 ФИКС. ЦЕНА"
                
                if pigeon.listing_type == 'auction':
                    price_info = f"💰 Текущая цена: *{pigeon.current_price} TJS*\n⏰ Окончание: {pigeon.auction_end_date.strftime('%d.%m.%Y %H:%M') if pigeon.auction_end_date else 'Не указано'}"
                else:
                    price_info = f"💰 Цена: *{pigeon.price} TJS*"
                
                location = pigeon.location if pigeon.location else "Не указана"
                seller_name = pigeon.owner.username
                description = pigeon.description[:500] if pigeon.description else "Описание отсутствует"
                
                details_text = (
                    f"{vip_badge}*{pigeon.title}*\n\n"
                    f"🏷️ Тип: {listing_type}\n"
                    f"{price_info}\n"
                    f"📍 Локация: {location}\n"
                    f"👤 Продавец: @{seller_name}\n"
                    f"👁 Просмотров: {pigeon.views_count}\n\n"
                    f"📝 *Описание:*\n{description}\n\n"
                    f"🔗 [Открыть на сайте](https://magaj.pythonanywhere.com/pigeon/{pigeon.id}/)"
                )
                
                # Create Buy Now button (WebApp to specific page)
                markup = types.InlineKeyboardMarkup()
                btn_buy = types.InlineKeyboardButton(
                    '🛒 Купить / Сделать ставку',
                    web_app=types.WebAppInfo(url=f'https://magaj.pythonanywhere.com/pigeon/{pigeon.id}/')
                )
                markup.add(btn_buy)
                markup.add(types.InlineKeyboardButton('🔙 Главное меню', callback_data='back_to_main'))
                
                # Send photo if exists
                if pigeon.image:
                    try:
                        photo_url = f"https://magaj.pythonanywhere.com{pigeon.image.url}"
                        bot.send_photo(
                            message.chat.id,
                            photo_url,
                            caption=details_text,
                            parse_mode='Markdown',
                            reply_markup=markup
                        )
                    except Exception as photo_error:
                        # If photo fails, send text only
                        self.stdout.write(self.style.WARNING(f'Photo error: {str(photo_error)}'))
                        bot.send_message(
                            message.chat.id,
                            details_text,
                            parse_mode='Markdown',
                            reply_markup=markup,
                            disable_web_page_preview=False
                        )
                else:
                    # No photo - send text only
                    bot.send_message(
                        message.chat.id,
                        details_text,
                        parse_mode='Markdown',
                        reply_markup=markup,
                        disable_web_page_preview=False
                    )
                    
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "❌ ID должен быть числом!\n\nИспользуйте: `/view_1`",
                    parse_mode='Markdown'
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'View error: {str(e)}'))
                bot.send_message(message.chat.id, "❌ Ошибка при загрузке голубя.")
        
        # ==================== START POLLING ====================
        
        self.stdout.write(self.style.SUCCESS('✅ Bot is running! Press Ctrl+C to stop.'))
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n⚠️ Bot stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Bot error: {str(e)}'))
