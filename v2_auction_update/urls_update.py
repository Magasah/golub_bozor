# ДОБАВЬ ЭТО В core/urls.py

from django.urls import path
from . import views

# Добавь этот маршрут в список urlpatterns:
"""
urlpatterns = [
    # ... существующие маршруты ...
    path('pigeon/<int:pigeon_id>/bid/', views.place_bid, name='place_bid'),
]
"""
