"""
URL configuration for core app
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Pigeon listings
    path('pigeon/<int:pk>/', views.pigeon_detail, name='pigeon_detail'),
    path('pigeon/add/', views.add_pigeon, name='add_pigeon'),
    path('pigeon/<int:pk>/edit/', views.edit_pigeon, name='edit_pigeon'),
    path('pigeon/<int:pk>/delete/', views.delete_pigeon, name='delete_pigeon'),
    path('my-pigeons/', views.my_pigeons, name='my_pigeons'),
    
    # Favorites
    path('pigeon/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # VIP placement
    path('vip-request/', views.vip_request, name='vip_request'),
    path('vip-payment/', views.vip_payment, name='vip_payment'),
    
    # Seller profile
    path('seller/<str:username>/', views.seller_profile, name='seller_profile'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='home'
    ), name='logout'),
]
