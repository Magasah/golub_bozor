"""
Django settings for GolubBozor project.
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Определяем, работаем ли мы на PythonAnywhere
ON_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-here-change-in-production')

# 🔒 SECURITY: DEBUG = False hides sensitive error pages and stack traces from users.
# CRITICAL: Never set DEBUG = True in production! It exposes secret keys, file paths, and SQL queries.
DEBUG = False  # Set to False for production security

# 🔒 SECURITY: Only allow requests from these domains (prevents host header attacks)
ALLOWED_HOSTS = ['magaj.pythonanywhere.com', 'localhost', '127.0.0.1']

# Для PythonAnywhere добавляем домен
if ON_PYTHONANYWHERE:
    ALLOWED_HOSTS.append(os.environ.get('PYTHONANYWHERE_DOMAIN', ''))


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
    'axes.backends.AxesStandaloneBackend',  # AxesStandaloneBackend should be first
    'django.contrib.auth.backends.ModelBackend',
]

AXES_FAILURE_LIMIT = 5  # Block after 5 failed attempts
AXES_COOLOFF_TIME = 1  # Block for 1 hour (in hours)
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]  # Lock by username + IP (new syntax)
AXES_RESET_ON_SUCCESS = True  # Reset counter on successful login

# Site domain for building absolute URLs (used in Telegram channel posting)
SITE_DOMAIN = 'http://127.0.0.1:8000'

# 🔒 SECURITY: Cookie security settings for HTTPS
# TODO: Set these to True when HTTPS is active on production
CSRF_COOKIE_SECURE = False  # Set to True when using HTTPS (prevents CSRF token theft)
SESSION_COOKIE_SECURE = False  # Set to True when using HTTPS (prevents session hijacking)
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF token
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SECURE_BROWSER_XSS_FILTER = True  # Enable browser XSS protection
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking attacks
