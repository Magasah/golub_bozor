"""
Views for GolubBozor - Pigeon Marketplace
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from .models import Pigeon
from .forms import PigeonForm, RegisterForm


def home(request):
    """
    Home page - displays only approved pigeon listings
    VIP pigeons are automatically shown first due to model ordering
    Supports filtering by breed, sex, and max price
    """
    # Only show approved pigeons
    pigeons = Pigeon.objects.filter(is_approved=True)
    
    # Search query
    search_query = request.GET.get('search', '')
    if search_query:
        pigeons = pigeons.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by breed
    breed_filter = request.GET.get('breed', '')
    if breed_filter:
        pigeons = pigeons.filter(breed=breed_filter)
    
    # Filter by sex
    sex_filter = request.GET.get('sex', '')
    if sex_filter:
        pigeons = pigeons.filter(sex=sex_filter)
    
    # Filter by game type
    game_type_filter = request.GET.get('game_type', '')
    if game_type_filter:
        pigeons = pigeons.filter(game_type=game_type_filter)
    
    # Filter by city
    city_filter = request.GET.get('city', '')
    if city_filter:
        pigeons = pigeons.filter(city=city_filter)
    
    # Filter by max price
    max_price = request.GET.get('max_price', '')
    if max_price:
        try:
            max_price_decimal = Decimal(max_price)
            pigeons = pigeons.filter(price__lte=max_price_decimal)
        except:
            pass
    
    context = {
        'pigeons': pigeons,
        'search_query': search_query,
        'breed_filter': breed_filter,
        'sex_filter': sex_filter,
        'game_type_filter': game_type_filter,
        'city_filter': city_filter,
        'max_price': max_price,
        'breed_choices': Pigeon.BREED_CHOICES,
        'sex_choices': Pigeon.SEX_CHOICES,
        'game_type_choices': Pigeon.GAME_TYPE_CHOICES,
        'city_choices': Pigeon.CITY_CHOICES,
    }
    return render(request, 'core/home.html', context)


def pigeon_detail(request, pk):
    """
    Detail view for a single pigeon listing
    Shows full information including breed, sex, game type, and contact options
    Increments view counter using F() expression to avoid race conditions
    """
    pigeon = get_object_or_404(Pigeon, pk=pk)
    
    # Increment views count atomically
    Pigeon.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
    
    # Refresh from database to get updated count
    pigeon.refresh_from_db()
    
    # Check if current user has favorited this pigeon
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = pigeon.favorites.filter(id=request.user.id).exists()
    
    context = {
        'pigeon': pigeon,
        'is_favorited': is_favorited,
    }
    return render(request, 'core/detail.html', context)


@login_required
def add_pigeon(request):
    """
    View for adding a new pigeon listing
    Requires user to be logged in
    New listings require moderation (is_approved=False by default)
    """
    if request.method == 'POST':
        form = PigeonForm(request.POST, request.FILES)
        if form.is_valid():
            pigeon = form.save(commit=False)
            pigeon.owner = request.user
            pigeon.is_approved = False  # Requires moderation
            pigeon.save()
            messages.warning(request, '⏳ Объявление отправлено на модерацию. Оно появится на сайте после проверки администратором.')
            return redirect('my_pigeons')
    else:
        form = PigeonForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/add_pigeon.html', context)


@login_required
def edit_pigeon(request, pk):
    """
    View for editing an existing pigeon listing
    Only owner can edit their listing
    After edit, requires re-moderation
    """
    pigeon = get_object_or_404(Pigeon, pk=pk)
    
    # Check if user is the owner
    if pigeon.owner != request.user:
        messages.error(request, 'Вы можете редактировать только свои объявления!')
        return redirect('pigeon_detail', pk=pk)
    
    if request.method == 'POST':
        form = PigeonForm(request.POST, request.FILES, instance=pigeon)
        if form.is_valid():
            pigeon = form.save(commit=False)
            pigeon.is_approved = False  # Requires re-moderation after edit
            pigeon.save()
            messages.warning(request, '⏳ Изменения отправлены на модерацию.')
            return redirect('my_pigeons')
    else:
        form = PigeonForm(instance=pigeon)
    
    context = {
        'form': form,
        'pigeon': pigeon,
    }
    return render(request, 'core/add_pigeon.html', context)


@login_required
def delete_pigeon(request, pk):
    """
    View for deleting a pigeon listing
    Only owner can delete their listing
    """
    pigeon = get_object_or_404(Pigeon, pk=pk)
    
    if pigeon.owner != request.user:
        messages.error(request, 'Вы можете удалить только свои объявления!')
        return redirect('pigeon_detail', pk=pk)
    
    if request.method == 'POST':
        pigeon.delete()
        messages.success(request, 'Объявление удалено!')
        return redirect('home')
    
    context = {
        'pigeon': pigeon,
    }
    return render(request, 'core/delete_confirm.html', context)


def register(request):
    """
    User registration view
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('home')
    else:
        form = RegisterForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/register.html', context)


@login_required
def my_pigeons(request):
    """
    View for displaying current user's pigeon listings
    Shows all listings (approved and pending)
    """
    pigeons = Pigeon.objects.filter(owner=request.user)
    
    context = {
        'pigeons': pigeons,
    }
    return render(request, 'core/my_pigeons.html', context)


def seller_profile(request, username):
    """
    Public seller profile view
    Shows seller's information and their approved listings
    """
    seller = get_object_or_404(User, username=username)
    
    # Only show approved listings on public profile
    approved_pigeons = Pigeon.objects.filter(
        owner=seller,
        is_approved=True
    )
    
    context = {
        'seller': seller,
        'pigeons': approved_pigeons,
        'pigeon_count': approved_pigeons.count(),
    }
    return render(request, 'core/profile.html', context)


@login_required
@require_POST
def toggle_favorite(request, pk):
    """
    Toggle favorite status for a pigeon listing
    Returns JSON response for AJAX requests
    """
    pigeon = get_object_or_404(Pigeon, pk=pk)
    
    # Check if already favorited
    if pigeon.favorites.filter(id=request.user.id).exists():
        # Remove from favorites
        pigeon.favorites.remove(request.user)
        is_favorited = False
        message = 'Удалено из избранного'
    else:
        # Add to favorites
        pigeon.favorites.add(request.user)
        is_favorited = True
        message = 'Добавлено в избранное'
    
    # Return JSON response
    return JsonResponse({
        'success': True,
        'is_favorited': is_favorited,
        'favorites_count': pigeon.favorites.count(),
        'message': message
    })


@login_required
def vip_request(request):
    """
    Static page explaining VIP placement and payment instructions
    Shows contact information and payment methods (Alif/DC wallet)
    """
    context = {
        'week_price': 7,  # Week price in TJS
        'month_price': 30,  # Month price in TJS
        'whatsapp_number': '+992888788181',
    }
    return render(request, 'core/vip_request.html', context)


def vip_payment(request):
    """
    VIP payment page with hardcoded pricing
    """
    context = {
        'week_price': 7,
        'month_price': 30,
        'whatsapp_number': '+992888788181',
    }
    return render(request, 'core/vip_payment.html', context)
