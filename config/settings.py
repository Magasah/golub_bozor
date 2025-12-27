"""
Django settings for GolubBozor project.
"""

from pathlib import Path
import os
import dj_database_url

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
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',  # Django Axes for brute force protection
    'core.apps.CoreConfig',  # Our main app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
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
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
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

LANGUAGE_CODE = 'ru-ru'

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
