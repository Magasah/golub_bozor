"""
Django settings for GolubBozor project.
"""

from pathlib import Path
import os
import dj_database_url
from django.utils.translation import gettext_lazy as _

# Загрузка переменных окружения из .env файла (для локальной разработки)
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Определяем, работаем ли мы на PythonAnywhere
ON_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# 🔒 ВАЖНО: Для продакшена создайте новый SECRET_KEY и добавьте в .env
# Генератор: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-+c6f7b^h9k@8_h$l!@8m6+9q9&^3u0x_y9k8j7h6g5f4d3s2a1')

# 🔒 SECURITY: DEBUG = False hides sensitive error pages and stack traces from users.
# CRITICAL: Never set DEBUG = True in production! It exposes secret keys, file paths, and SQL queries.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# 🔒 SECURITY: Only allow requests from these domains (prevents host header attacks)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Для PythonAnywhere добавляем домен
if ON_PYTHONANYWHERE:
    pythonanywhere_domain = os.environ.get('PYTHONANYWHERE_DOMAIN', '')
    if pythonanywhere_domain and pythonanywhere_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(pythonanywhere_domain)


# Application definition

INSTALLED_APPS = [
    'unfold',  # 🎨 Modern admin interface (must be before django.contrib.admin)
    'unfold.contrib.filters',  # Advanced filters for admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',   # sitemap.xml
    'axes',  # Django Axes for brute force protection
    'core.apps.CoreConfig',  # Our main app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Для мультиязычности (i18n)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',  # Django Axes for brute force protection
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'core.context_processors.get_holiday_theme',  # Праздничные темы
                'core.context_processors.site_context',  # Общий контекст сайта
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email', 'first_name', 'last_name'),
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru'

LANGUAGES = [
    ('ru', _('Русский')),
    ('tg', _('Тоҷикӣ')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Asia/Dushanbe'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise configuration for static files (без Manifest для избежания ошибок)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login redirect
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'

# Django Axes settings for brute force protection
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',  # AxesBackend should be first (for django-axes)
    'django.contrib.auth.backends.ModelBackend',  # Standard Django authentication
]

AXES_FAILURE_LIMIT = 5  # Block after 5 failed attempts
AXES_COOLOFF_TIME = 1  # Block for 1 hour (in hours)
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]  # Lock by username + IP (new syntax)
AXES_RESET_ON_SUCCESS = True  # Reset counter on successful login

# Site domain for building absolute URLs (used in Telegram channel posting)
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', 'http://127.0.0.1:8000')

# 🔒 SECURITY: Cookie security settings for HTTPS
# Эти настройки автоматически включаются для продакшена
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'

# Всегда включены (безопасны для любого окружения)
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF token
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SECURE_BROWSER_XSS_FILTER = True  # Enable browser XSS protection
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking attacks

# HSTS (включать только на продакшене с HTTPS)
if not DEBUG and SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = 31536000  # 1 год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# ========== EMAIL CONFIGURATION (для восстановления пароля) ==========
# Настройки SMTP для отправки писем
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Gmail SMTP (пример - замените на свои данные)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')  # Ваш email
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')  # Пароль приложения
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Для тестирования (отображает письма в консоли вместо отправки)
if DEBUG and not EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ========== PASSWORD RESET SETTINGS ==========
# URLs для восстановления пароля
PASSWORD_RESET_TIMEOUT = 3600  # Ссылка действительна 1 час (3600 секунд)


# ========== JAZZMIN ADMIN THEME SETTINGS ==========
JAZZMIN_SETTINGS = {
    # Заголовки
    "site_title": "ЗооБозор Admin",
    "site_header": "ЗооБозор",
    "site_brand": "🦁 ЗооБозор",
    "site_logo": None,  # Путь к логотипу (опционально)
    "login_logo": None,
    "site_icon": None,
    
    # Welcome text на главной
    "welcome_sign": "Добро пожаловать в админ-панель ЗооБозор",
    
    # Copyright
    "copyright": "ЗооБозор © 2024",
    
    # Поиск в админке
    "search_model": ["core.Animal", "auth.User"],
    
    # Темная тема
    "theme": "darkly",
    
    # Показывать UI Builder
    "show_ui_builder": False,
    
    # Sidebar
    "show_sidebar": True,
    "navigation_expanded": False,
    
    # Top Menu
    "topmenu_links": [
        {"name": "Главная страница", "url": "/", "new_window": False},
        {"name": "Поддержка", "url": "https://t.me/Magasah", "new_window": True},
    ],
    
    # User Menu
    "usermenu_links": [
        {"model": "auth.user"}
    ],
    
    # Иконки для моделей
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.Animal": "fas fa-paw",
        "core.AnimalImage": "fas fa-images",
        "core.UserProfile": "fas fa-id-card",
        "core.Review": "fas fa-star",
        "core.Comment": "fas fa-comments",
        "core.Bid": "fas fa-gavel",
        "core.Veterinarian": "fas fa-user-md",
    },
    
    # Порядок отображения приложений
    "order_with_respect_to": [
        "core",
        "core.animal",
        "core.userprofile",
        "auth",
    ],
    
    # Кастомные ссылки
    "custom_links": {
        "core": [{
            "name": "Статистика", 
            "url": "/admin/",
            "icon": "fas fa-chart-line",
        }]
    },
    
    # Hide apps/models
    "hide_apps": [],
    "hide_models": [],
    
    # Related modal
    "related_modal_active": True,
    
    # Custom CSS/JS
    "custom_css": None,
    "custom_js": None,
    
    # Формат changeform
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

# UI Tweaks для кастомизации стилей
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-warning",  # Золотой акцент
    "navbar": "navbar-dark navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-warning",  # Темная sidebar с золотым
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "darkly",  # Темная тема
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# ========================================
# DJANGO UNFOLD CONFIGURATION
# ========================================
UNFOLD = {
    "SITE_TITLE": "ZooBozor Admin",
    "SITE_HEADER": "ZooBozor Control Panel",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "🐾",
        "dark": lambda request: "🐾",
    },
    
    # Sidebar navigation
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Главная",
                "items": [
                    {
                        "title": "Сайт",
                        "icon": "home",
                        "link": "/",
                    },
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "Управление контентом",
                "separator": True,
                "items": [
                    {
                        "title": "Животные",
                        "icon": "pets",
                        "link": lambda request: "/admin/core/animal/",
                    },
                    {
                        "title": "Зоо-Такси",
                        "icon": "local_shipping",
                        "link": lambda request: "/admin/core/animal/?category__exact=transport",
                    },
                    {
                        "title": "Предложения цен",
                        "icon": "attach_money",
                        "link": lambda request: "/admin/core/offer/",
                    },
                    {
                        "title": "Ставки (Аукцион)",
                        "icon": "gavel",
                        "link": lambda request: "/admin/core/bid/",
                    },
                    {
                        "title": "Комментарии",
                        "icon": "comment",
                        "link": lambda request: "/admin/core/comment/",
                    },
                ],
            },
            {
                "title": "Пользователи",
                "separator": True,
                "items": [
                    {
                        "title": "Пользователи",
                        "icon": "person",
                        "link": lambda request: "/admin/auth/user/",
                    },
                    {
                        "title": "Группы",
                        "icon": "group",
                        "link": lambda request: "/admin/auth/group/",
                    },
                    {
                        "title": "Профили",
                        "icon": "account_circle",
                        "link": lambda request: "/admin/core/userprofile/",
                    },
                ],
            },
            {
                "title": "Финансы",
                "separator": True,
                "items": [
                    {
                        "title": "Платежи (Аукционы)",
                        "icon": "payment",
                        "link": lambda request: "/admin/core/animal/?is_paid__exact=1",
                    },
                    {
                        "title": "VIP объявления",
                        "icon": "star",
                        "link": lambda request: "/admin/core/animal/?is_vip__exact=1",
                    },
                ],
            },
        ],
    },
    
    # Colors (Black & Gold Theme)
    "COLORS": {
        "primary": {
            "50": "#FFF9E5",
            "100": "#FFF3CC",
            "200": "#FFE799",
            "300": "#FFDB66",
            "400": "#F4CF33",
            "500": "#D4AF37",  # Gold
            "600": "#B5952F",
            "700": "#967B27",
            "800": "#77621F",
            "900": "#584817",
        },
        "font": {
            "subtle-light": "#666666",
            "default-light": "#000000",
            "important-light": "#000000",
            "subtle-dark": "#999999",
            "default-dark": "#CCCCCC",
            "important-dark": "#FFFFFF",
        },
    },
    
    # Theme settings
    "STYLES": [
        lambda request: "css/unfold-custom.css",
    ],
    
    "SCRIPTS": [],
    
    # Dashboard
    "DASHBOARD_CALLBACK": None,
    
    # Extensions
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "ru": "🇷🇺",
                "tj": "🇹🇯",
            },
        },
    },
    
    # Environment badge
    "ENVIRONMENT": "config.settings.environment_callback",
    
    # Login customization
    "LOGIN": {
        "image": lambda request: "/static/img/logo.png",
        "redirect_after": lambda request: "/admin/",
    },
}

def environment_callback(request):
    """Show environment badge in admin"""
    if DEBUG:
        return ["Development", "red"]
    return ["Production", "green"]


