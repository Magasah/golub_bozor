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
    
    # Auction bidding
    path('pigeon/<int:pk>/bid/', views.place_bid, name='place_bid'),
    
    # Favorites
    path('pigeon/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites, name='favorites'),
    
    # VIP placement
    path('vip-request/', views.vip_request, name='vip_request'),
    path('vip-payment/', views.vip_payment, name='vip_payment'),
    
    # Seller profile
    path('seller/<str:username>/', views.seller_profile, name='seller_profile'),
    path('review/delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('review/delete/<int:pk>/', views.delete_review, name='delete_review'),
    
    # User settings
    path('settings/', views.user_settings, name='user_settings'),
    
    # Admin Dashboard (Custom)
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Manager Dashboard
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/approve/<int:pigeon_id>/', views.approve_payment, name='approve_payment'),
    path('manager/reject/<int:pigeon_id>/', views.reject_payment, name='reject_payment'),
    
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
