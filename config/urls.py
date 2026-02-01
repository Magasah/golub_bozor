"""
URL configuration for GolubBozor project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # i18n URL для смены языка
    path('i18n/', include('django.conf.urls.i18n')),
]

# Основные URL patterns с поддержкой языков
urlpatterns += i18n_patterns(
    # 🔒 SECURITY: Secret admin path. Do not share this URL publicly.
    # Use this URL to access admin: /control_panel_secret_7828/
    path('control_panel_secret_7828/', admin.site.urls),
    path('', include('core.urls')),
    prefix_default_language=False,
)

# Custom error handlers for production
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
