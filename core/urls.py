"""
URL configuration for core app
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Animal listings
    path('animal/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('animal/add/', views.add_animal, name='add_animal'),
    path('load-category-fields/', views.load_category_fields, name='load_category_fields'),  # HTMX
    path('get-animal-fields/', views.get_animal_fields, name='get_animal_fields'),  # HTMX для динамических полей
    path('animal/<int:pk>/edit/', views.edit_animal, name='edit_animal'),
    path('animal/<int:pk>/delete/', views.delete_animal, name='delete_animal'),
    path('my-animals/', views.my_animals, name='my_animals'),
    
    # Auction bidding (только для голубей)
    path('animal/<int:pk>/bid/', views.place_bid, name='place_bid'),
    
    # Comments
    path('animal/<int:pk>/comment/', views.add_comment, name='add_comment'),
    
    # Smart Offer (Price negotiation)
    path('animal/<int:pk>/offer/', views.create_offer, name='create_offer'),
    
    # Favorites
    path('animal/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('animal/<int:pk>/favorite-htmx/', views.toggle_favorite_htmx, name='toggle_favorite_htmx'),
    path('favorites/', views.favorites, name='favorites'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('animal/<int:pk>/mark-sold/', views.mark_as_sold, name='mark_as_sold'),
    
    # VIP placement
    path('vip-request/', views.vip_request, name='vip_request'),
    path('vip-payment/', views.vip_payment, name='vip_payment'),
    
    # Seller profile
    path('seller/<str:username>/', views.seller_profile, name='seller_profile'),
    path('review/delete/<int:pk>/', views.delete_review, name='delete_review'),
    
    # User settings
    path('settings/', views.user_settings, name='user_settings'),
    
    # Admin Dashboard (Custom) - renamed to avoid conflict
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # Manager Dashboard
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/approve/<int:animal_id>/', views.approve_payment, name='approve_payment'),
    path('manager/reject/<int:animal_id>/', views.reject_payment, name='reject_payment'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('email-verify/<uidb64>/<token>/', views.email_verify, name='email_verify'),  # Email verification
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='home'
    ), name='logout'),
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Veterinarians
    path('veterinarians/', views.veterinarians_list, name='veterinarians_list'),
    path('veterinarian/<int:pk>/', views.veterinarian_detail, name='veterinarian_detail'),
    path('veterinarian/add/', views.add_veterinarian, name='add_veterinarian'),
    path('veterinarian/<int:pk>/edit/', views.edit_veterinarian, name='edit_veterinarian'),
    path('veterinarian/<int:pk>/delete/', views.delete_veterinarian, name='delete_veterinarian'),
]
