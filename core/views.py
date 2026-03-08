"""
Views for ZooBozor - Animal Marketplace
Полностью обновленные views для новой модели Animal
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from .models import Animal, AnimalImage, Veterinarian, Bid, Review, Comment, UserProfile, Offer
from .forms import (
    AnimalSearchForm, AnimalForm, AnimalImageForm, BidForm,
    VeterinarianSearchForm, VeterinarianForm, ReviewForm, CommentForm,
    UserRegistrationForm
)
from .utils import send_telegram_message
import os


def home(request):
    """
    Main page with animal listings and filters
    Supports HTMX for dynamic filtering
    """
    # Get filter form
    form = AnimalSearchForm(request.GET or None)
    
    # Base queryset - only approved animals
    animals = Animal.objects.filter(is_approved=True).select_related('owner').prefetch_related('gallery')
    
    # Apply filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        city = form.cleaned_data.get('city')
        gender = form.cleaned_data.get('gender')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        listing_type = form.cleaned_data.get('listing_type')
        
        # Improved search with Q objects (searches in title, description, and breed)
        if search:
            animals = animals.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(breed__icontains=search)
            )
        
        if category:
            animals = animals.filter(category=category)
        
        if city:
            animals = animals.filter(city=city)
        
        if gender:
            animals = animals.filter(gender=gender)
        
        if price_min:
            animals = animals.filter(price__gte=price_min)
        
        if price_max:
            animals = animals.filter(price__lte=price_max)
        
        if listing_type:
            animals = animals.filter(listing_type=listing_type)
    
    # VIP animals first, then by date
    animals = animals.order_by('-is_vip', '-created_at')
    
    # Pagination
    paginator = Paginator(animals, 12)
    page_number = request.GET.get('page')
    animals_page = paginator.get_page(page_number)
    
    # Count by categories for stats
    category_counts = Animal.objects.filter(is_approved=True).values('category').annotate(count=Count('id'))
    
    context = {
        'animals': animals_page,
        'form': form,
        'category_counts': category_counts,
        'total_animals': animals.count(),
    }
    
    # Check if this is an HTMX request
    if request.headers.get('HX-Request'):
        # Return only the partial template for HTMX
        return render(request, 'core/_animal_list.html', context)
    
    # Return full page for normal requests
    return render(request, 'core/home.html', context)


def animal_detail(request, pk):
    """
    Animal detail page with comments and bidding
    """
    animal = get_object_or_404(
        Animal.objects.select_related('owner', 'owner__profile').prefetch_related('gallery', 'comments__author'),
        pk=pk
    )
    
    # Increment view count
    animal.views_count += 1
    animal.save(update_fields=['views_count'])
    
    # Get comments
    comments = animal.comments.all().order_by('-created_at')
    
    # Bid form for auctions (только для голубей)
    bid_form = None
    bids = []
    if animal.listing_type == 'auction' and animal.is_auction_active():
        bid_form = BidForm()
        bids = animal.bids.select_related('bidder').order_by('-created_at')[:10]
    
    # Comment form
    comment_form = CommentForm()
    
    # Check if in favorites
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = animal.favorites.filter(id=request.user.id).exists()
    
    # Similar animals (same category, different listing)
    similar_animals = Animal.objects.filter(
        category=animal.category,
        is_approved=True
    ).exclude(pk=animal.pk).order_by('-is_vip', '-created_at')[:6]
    
    context = {
        'animal': animal,
        'comments': comments,
        'comment_form': comment_form,
        'bid_form': bid_form,
        'bids': bids,
        'is_favorite': is_favorite,
        'similar_animals': similar_animals,
    }
    
    return render(request, 'core/animal_detail.html', context)


@login_required
def add_animal(request):
    """
    🆕 Создание объявления с динамической формой (HTMX)
    """
    from .forms import AnimalForm
    
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        
        if form.is_valid():
            animal = form.save(commit=False)
            animal.owner = request.user
            animal.is_approved = False  # Требует модерации
            
            try:
                animal.save()
                
                # Обработка дополнительных изображений
                images = request.FILES.getlist('extra_images')
                for image in images:
                    AnimalImage.objects.create(animal=animal, image=image)
                
                messages.success(request, '✅ Объявление создано! Ожидает модерации.')
                return redirect('animal_detail', pk=animal.pk)
            
            except Exception as e:
                messages.error(request, f'❌ Ошибка: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AnimalForm()
    
    return render(request, 'core/add_animal.html', {'form': form})


def load_category_fields(request):
    """
    🎯 HTMX view: Загружает специфичные поля для выбранной категории
    """
    category = request.GET.get('category', '')
    
    # Определяем какие поля показывать
    context = {'category': category}
    
    return render(request, 'core/partials/form_fields.html', context)


@login_required
def edit_animal(request, pk):
    """
    Edit existing animal listing
    """
    animal = get_object_or_404(Animal, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        
        if form.is_valid():
            try:
                animal = form.save()
                
                # Handle new images
                images = request.FILES.getlist('extra_images')
                for image in images:
                    AnimalImage.objects.create(animal=animal, image=image)
                
                messages.success(request, '✅ Объявление обновлено!')
                return redirect('animal_detail', pk=animal.pk)
            
            except Exception as e:
                messages.error(request, f'Ошибка: {str(e)}')
    else:
        form = AnimalForm(instance=animal)
    
    context = {
        'form': form,
        'animal': animal,
    }
    
    return render(request, 'core/edit_animal.html', context)


@login_required
def delete_animal(request, pk):
    """
    Delete animal listing
    """
    animal = get_object_or_404(Animal, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        animal.delete()
        messages.success(request, '🗑️ Объявление удалено!')
        return redirect('my_animals')
    
    return render(request, 'core/delete_animal.html', {'animal': animal})


@login_required
def my_animals(request):
    """
    User's own animal listings
    """
    animals = Animal.objects.filter(owner=request.user).order_by('-created_at')
    bids = Bid.objects.filter(bidder=request.user).select_related('animal').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(animals, 10)
    page_number = request.GET.get('page')
    animals_page = paginator.get_page(page_number)
    
    context = {
        'animals': animals_page,
        'listings_count': animals.count(),
        'bids_count': bids.count(),
    }
    
    return render(request, 'core/my_animals.html', context)


@login_required
def place_bid(request, pk):
    """
    Place bid on pigeon auction (only for pigeons!)
    """
    animal = get_object_or_404(Animal, pk=pk)
    
    # Validation: auction must be for pigeons only
    if animal.category != 'pigeon':
        messages.error(request, '❌ Аукционы доступны только для голубей!')
        return redirect('animal_detail', pk=pk)
    
    if not animal.is_auction_active():
        messages.error(request, '❌ Аукцион завершён или неактивен!')
        return redirect('animal_detail', pk=pk)
    
    if animal.owner == request.user:
        messages.error(request, '❌ Нельзя делать ставки на собственный аукцион!')
        return redirect('animal_detail', pk=pk)
    
    if request.method == 'POST':
        form = BidForm(request.POST)
        
        if form.is_valid():
            bid_amount = form.cleaned_data['amount']
            
            # Check if bid is higher than current price
            if bid_amount <= animal.current_price:
                messages.error(request, f'❌ Ставка должна быть выше текущей цены ({animal.current_price} TJS)!')
                return redirect('animal_detail', pk=pk)
            
            # Create bid
            bid = form.save(commit=False)
            bid.animal = animal
            bid.bidder = request.user
            bid.save()
            
            # Update animal's current price
            animal.current_price = bid_amount
            animal.save(update_fields=['current_price'])
            
            messages.success(request, f'✅ Ставка {bid_amount} TJS принята!')
            return redirect('animal_detail', pk=pk)
    
    return redirect('animal_detail', pk=pk)


@login_required
def toggle_favorite(request, pk):
    """
    Add/remove animal from favorites
    """
    animal = get_object_or_404(Animal, pk=pk)
    
    if request.user in animal.favorites.all():
        animal.favorites.remove(request.user)
        messages.info(request, '💔 Удалено из избранного')
    else:
        animal.favorites.add(request.user)
        messages.success(request, '❤️ Добавлено в избранное')
    
    return redirect('animal_detail', pk=pk)


@login_required
def favorites(request):
    """
    User's favorite animals
    """
    animals = request.user.favorite_animals.filter(is_approved=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(animals, 12)
    page_number = request.GET.get('page')
    animals_page = paginator.get_page(page_number)
    
    context = {
        'animals': animals_page,
    }
    
    return render(request, 'core/favorites.html', context)


@login_required
def dashboard(request):
    """
    Comprehensive user profile dashboard with all user-related data
    Tabs: Listings, Bids, Favorites, Reviews, Settings
    """
    user = request.user
    
    # Get user's animals
    my_animals = Animal.objects.filter(owner=user).order_by('-created_at')
    
    # Get user's bids
    my_bids = Bid.objects.filter(bidder=user).select_related('animal').order_by('-created_at')
    
    # Get favorites
    favorites = user.favorite_animals.filter(is_approved=True).order_by('-created_at')
    
    # Get reviews about user (as seller)
    reviews = Review.objects.filter(seller=user).select_related('buyer').order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Statistics
    listings_count = my_animals.count()
    bids_count = my_bids.count()
    favorites_count = favorites.count()
    review_count = reviews.count()
    
    context = {
        'my_animals': my_animals,
        'my_bids': my_bids,
        'favorites': favorites,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'review_count': review_count,
        'listings_count': listings_count,
        'bids_count': bids_count,
        'favorites_count': favorites_count,
    }
    
    return render(request, 'core/my_profile.html', context)


@login_required
@require_POST
def mark_as_sold(request, pk):
    """
    Mark animal as sold
    """
    animal = get_object_or_404(Animal, pk=pk, owner=request.user)
    animal.status = 'sold'
    animal.save()
    
    # Update user's total sales
    profile = request.user.profile
    profile.total_sales += 1
    profile.save()
    
    # Check for verification eligibility
    sold_count = Animal.objects.filter(owner=request.user, status='sold').count()
    if sold_count >= 3 and not profile.is_verified:
        messages.success(
            request,
            '🎉 Поздравляем! Вы продали более 3 товаров. Получите знак доверенного продавца! '
            'Свяжитесь с администратором.'
        )
    else:
        messages.success(request, '✅ Объявление отмечено как проданное')
    
    return redirect('dashboard')


@login_required
@require_http_methods(["POST"])
def toggle_favorite_htmx(request, pk):
    """
    Add/remove animal from favorites (HTMX version)
    Returns HTML fragment
    """
    animal = get_object_or_404(Animal, pk=pk)
    
    is_favorite = request.user in animal.favorites.all()
    
    if is_favorite:
        animal.favorites.remove(request.user)
    else:
        animal.favorites.add(request.user)
    
    # Return updated button HTML
    favorites_count = animal.favorites.count()
    context = {
        'animal': animal,
        'is_favorite': not is_favorite,
        'favorites_count': favorites_count,
    }
    
    return render(request, 'core/partials/favorite_button.html', context)


def veterinarians_list(request):
    """
    Veterinarians and clinics directory
    """
    form = VeterinarianSearchForm(request.GET or None)
    
    vets = Veterinarian.objects.filter(is_approved=True)
    
    # Apply filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        city = form.cleaned_data.get('city')
        
        if search:
            vets = vets.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        if city:
            vets = vets.filter(city=city)
    
    # VIP first, then by date
    vets = vets.order_by('-is_vip', '-created_at')
    
    # Pagination
    paginator = Paginator(vets, 9)
    page_number = request.GET.get('page')
    vets_page = paginator.get_page(page_number)
    
    context = {
        'veterinarians': vets_page,
        'form': form,
    }
    
    return render(request, 'core/veterinarians.html', context)


def veterinarian_detail(request, pk):
    """
    Veterinarian detail page
    """
    vet = get_object_or_404(Veterinarian, pk=pk, is_approved=True)
    
    context = {
        'vet': vet,
    }
    
    return render(request, 'core/veterinarian_detail.html', context)


@login_required
def add_veterinarian(request):
    """
    Add veterinarian/clinic
    """
    if request.method == 'POST':
        form = VeterinarianForm(request.POST, request.FILES)
        
        if form.is_valid():
            vet = form.save(commit=False)
            vet.is_approved = False  # Requires moderation
            vet.save()
            
            messages.success(request, '✅ Ветклиника добавлена! Ожидает модерации.')
            return redirect('veterinarians_list')
    else:
        form = VeterinarianForm()
    
    return render(request, 'core/add_veterinarian.html', {'form': form})


@login_required
def add_comment(request, pk):
    """
    Add comment to animal listing
    """
    animal = get_object_or_404(Animal, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.animal = animal
            comment.author = request.user
            comment.save()
            
            messages.success(request, '✅ Комментарий добавлен!')
    
    return redirect('animal_detail', pk=pk)


def profile(request, username):
    """
    Public user profile with their animals and reviews
    """
    user = get_object_or_404(User, username=username)
    profile_obj = user.profile
    
    # User's animals
    animals = Animal.objects.filter(owner=user, is_approved=True).order_by('-created_at')[:6]
    
    # Reviews about this seller
    reviews = Review.objects.filter(seller=user).select_related('buyer').order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'profile_user': user,
        'profile': profile_obj,
        'animals': animals,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 2),
    }
    
    return render(request, 'core/profile.html', context)


def register(request):
    """
    🔒 Регистрация с email-верификацией
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            # Сохраняем пользователя (is_active=False)
            user = form.save()
            
            # Отправляем письмо с верификацией
            from .email_utils import send_verification_email
            try:
                send_verification_email(request, user)
                messages.success(
                    request, 
                    f'📧 Регистрация почти завершена! Мы отправили письмо на {user.email}. '
                    'Проверьте почту и перейдите по ссылке для активации аккаунта.'
                )
            except Exception as e:
                # Если письмо не отправилось, удаляем пользователя
                user.delete()
                messages.error(
                    request, 
                    '❌ Ошибка отправки письма. Проверьте email и попробуйте снова.'
                )
                return render(request, 'core/register.html', {'form': form})
            
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})


def email_verify(request, uidb64, token):
    """
    🔒 Верификация email по токену
    """
    from .email_utils import verify_email_token
    
    user = verify_email_token(uidb64, token)
    
    if user:
        user.is_active = True
        user.save()
        messages.success(
            request, 
            f'✅ Email подтвержден! Добро пожаловать в ЗооБозор, {user.username}!'
        )
        login(request, user)
        return redirect('home')
    else:
        messages.error(
            request, 
            '❌ Ссылка активации недействительна или устарела.'
        )
        return redirect('login')


from django.contrib.auth.models import User


@login_required
def user_settings(request):
    """
    User settings view where users can update their Telegram chat ID
    """
    from .models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        telegram_chat_id = request.POST.get('telegram_chat_id', '').strip()
        profile.telegram_chat_id = telegram_chat_id if telegram_chat_id else None
        profile.save()
        
        if telegram_chat_id:
            messages.success(request, '✅ Telegram ID сохранён! Вы будете получать уведомления.')
        else:
            messages.success(request, '✅ Telegram ID удалён. Уведомления отключены.')
        
        return redirect('user_settings')
    
    context = {
        'profile': profile,
    }
    return render(request, 'core/settings.html', context)


def seller_profile(request, username):
    """
    Public seller profile view
    Shows seller's information and their approved listings
    Includes rating/review system
    """
    seller = get_object_or_404(User, username=username)
    
    # Only show approved listings on public profile
    approved_animals = Animal.objects.filter(
        owner=seller,
        is_approved=True
    )
    
    # Calculate average rating
    reviews = Review.objects.filter(seller=seller)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    review_count = reviews.count()
    
    # Generate star display for average rating
    if avg_rating:
        full_stars = int(avg_rating)
        half_star = 1 if (avg_rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        stars_display = '⭐' * full_stars + ('½' if half_star else '') + '☆' * empty_stars
        avg_rating = round(avg_rating, 1)
    else:
        stars_display = '☆☆☆☆☆'
        avg_rating = 0
    
    # Handle review submission
    review_form = None
    user_has_reviewed = False
    can_review = False
    
    if request.user.is_authenticated:
        # Check if user already reviewed this seller
        user_has_reviewed = Review.objects.filter(seller=seller, buyer=request.user).exists()
        # User can review if: not themselves, authenticated, and hasn't reviewed yet
        can_review = request.user != seller and not user_has_reviewed
        
        if request.method == 'POST':
            # Double-check user cannot review themselves
            if request.user == seller:
                messages.error(request, '❌ Вы не можете оставить отзыв самому себе.')
                return redirect('seller_profile', username=username)
            
            if user_has_reviewed:
                messages.warning(request, '⚠️ Вы уже оставили отзыв этому продавцу.')
                return redirect('seller_profile', username=username)
            
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.seller = seller
                review.buyer = request.user
                try:
                    review.save()
                    messages.success(request, '✅ Спасибо за ваш отзыв!')
                    return redirect('seller_profile', username=username)
                except Exception as e:
                    messages.error(request, '❌ Ошибка при сохранении отзыва.')
        elif can_review:
            review_form = ReviewForm()
    
    context = {
        'seller': seller,
        'animals': approved_animals,
        'animal_count': approved_animals.count(),
        'reviews': reviews[:10],  # Show last 10 reviews
        'review_count': review_count,
        'avg_rating': avg_rating,
        'stars_display': stars_display,
        'review_form': review_form,
        'can_review': can_review,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'core/profile.html', context)


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


def admin_dashboard(request):
    """
    Custom Admin Dashboard - Command Center
    High-level analytics and recent activity for site owners
    """
    # ==================== STATISTICS ====================
    
    # Total counts
    total_users = User.objects.count()
    total_animals = Animal.objects.count()
    
    # Active auctions (listing_type='auction', not sold, not expired)
    active_auctions = Animal.objects.filter(
        listing_type='auction',
        is_approved=True,
        is_sold=False,
        auction_end_date__gt=timezone.now()
    ).count()
    
    # Pending payment approvals
    pending_approvals = Animal.objects.filter(
        listing_type='auction',
        is_paid=False,
        payment_receipt__isnull=False
    ).exclude(payment_receipt='').count()
    
    # Total revenue (paid auctions * 3 TJS per auction)
    paid_auctions_count = Animal.objects.filter(
        listing_type='auction',
        is_paid=True
    ).count()
    total_revenue = paid_auctions_count * 3
    
    # ==================== RECENT ACTIVITY ====================
    
    # Last 5 registered users
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Last 5 added animals
    recent_animals = Animal.objects.select_related('owner').order_by('-created_at')[:5]
    
    # Additional analytics
    approved_animals = Animal.objects.filter(is_approved=True).count()
    pending_animals = Animal.objects.filter(is_approved=False).count()
    vip_animals = Animal.objects.filter(is_vip=True).count()
    sold_animals = Animal.objects.filter(is_sold=True).count()
    
    context = {
        # Main statistics
        'total_users': total_users,
        'total_animals': total_animals,
        'active_auctions': active_auctions,
        'pending_approvals': pending_approvals,
        'total_revenue': total_revenue,
        
        # Additional stats
        'approved_animals': approved_animals,
        'pending_animals': pending_animals,
        'vip_animals': vip_animals,
        'sold_animals': sold_animals,
        
        # Recent activity
        'recent_users': recent_users,
        'recent_animals': recent_animals,
    }
    
    return render(request, 'core/custom_dashboard.html', context)


@staff_member_required
def manager_dashboard(request):
    """
    Manager Dashboard - Review pending auction payment receipts
    Only accessible to staff users
    """
    # Fetch all auctions with receipts pending approval
    pending_payments = Animal.objects.filter(
        listing_type='auction',
        is_paid=False,
        payment_receipt__isnull=False
    ).exclude(payment_receipt='').select_related('owner').order_by('-created_at')
    
    context = {
        'pending_payments': pending_payments,
        'pending_count': pending_payments.count(),
    }
    return render(request, 'core/manager_dashboard.html', context)


@staff_member_required
@require_POST
def approve_payment(request, animal_id):
    """
    Approve auction payment receipt
    Marks payment as approved and notifies user via Telegram
    """
    animal = get_object_or_404(Animal, pk=animal_id, listing_type='auction')
    
    # Mark as paid
    animal.is_paid = True
    animal.save()
    
    # Notify user via Telegram
    try:
        profile = UserProfile.objects.filter(user=animal.owner).first()
        if profile and profile.telegram_chat_id:
            message = (
                f"✅ *Оплата принята!*\n\n"
                f"Ваш аукцион *{animal.title}* успешно запущен.\n\n"
                f"Стартовая цена: `{animal.start_price} TJS`\n"
                f"Дата окончания: `{animal.auction_end_date.strftime('%d.%m.%Y %H:%M')}`\n\n"
                f"Удачных торгов! 🦁"
            )
            send_telegram_message(profile.telegram_chat_id, message)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
    
    messages.success(request, f'Оплата для аукциона "{animal.title}" одобрена!')
    return redirect('manager_dashboard')


@staff_member_required
@require_POST
def reject_payment(request, animal_id):
    """
    Reject auction payment receipt
    Deletes receipt file and notifies user via Telegram
    """
    animal = get_object_or_404(Animal, pk=animal_id, listing_type='auction')
    
    # Delete receipt file if exists
    if animal.payment_receipt:
        if os.path.isfile(animal.payment_receipt.path):
            os.remove(animal.payment_receipt.path)
        animal.payment_receipt = None
        animal.save()
    
    # Notify user via Telegram
    try:
        profile = UserProfile.objects.filter(user=animal.owner).first()
        if profile and profile.telegram_chat_id:
            message = (
                f"❌ *Оплата отклонена*\n\n"
                f"К сожалению, чек для аукциона *{animal.title}* был отклонен.\n\n"
                f"*Причина:* Чек нечитаем или сумма неверна.\n\n"
                f"Пожалуйста, загрузите новый чек оплаты через форму редактирования объявления.\n\n"
                f"Требуемая сумма: `3 TJS`\n"
                f"Номер для оплаты: `+992 888 788 181`"
            )
            send_telegram_message(profile.telegram_chat_id, message)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
    
    messages.warning(request, f'Оплата для аукциона "{animal.title}" отклонена. Пользователь уведомлен.')
    return redirect('manager_dashboard')


@staff_member_required
@require_POST
def delete_review(request, pk):
    """
    Delete review (only for staff/admin)
    """
    review = get_object_or_404(Review, pk=pk)
    seller_username = review.seller.username
    
    # Store info before deletion
    author_name = review.author.username
    review_text = review.text[:50] if review.text else 'Без комментария'
    
    review.delete()
    
    messages.success(request, f'Отзыв от {author_name} удалён: "{review_text}"')
    return redirect('seller_profile', username=seller_username)


def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, 'core/404.html', status=404)


def custom_500(request):
    """Custom 500 error page"""
    return render(request, 'core/500.html', status=500)


@login_required
def edit_veterinarian(request, pk):
    """Edit veterinarian (owner only)"""
    vet = get_object_or_404(Veterinarian, pk=pk)
    
    # Only allow owner or staff to edit
    if vet.added_by != request.user and not request.user.is_staff:
        messages.error(request, '❌ У вас нет прав для редактирования этого ветеринара')
        return redirect('veterinarian_detail', pk=pk)
    
    if request.method == 'POST':
        form = VeterinarianForm(request.POST, request.FILES, instance=vet)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Информация о ветеринаре обновлена')
            return redirect('veterinarian_detail', pk=pk)
    else:
        form = VeterinarianForm(instance=vet)
    
    return render(request, 'core/edit_veterinarian.html', {'form': form, 'vet': vet})


@login_required
def delete_veterinarian(request, pk):
    """Delete veterinarian (owner only)"""
    vet = get_object_or_404(Veterinarian, pk=pk)
    
    # Only allow owner or staff to delete
    if vet.added_by != request.user and not request.user.is_staff:
        messages.error(request, '❌ У вас нет прав для удаления этого ветеринара')
        return redirect('veterinarian_detail', pk=pk)
    
    if request.method == 'POST':
        vet.delete()
        messages.success(request, '✅ Ветеринар удалён')
        return redirect('veterinarians_list')
    
    return render(request, 'core/delete_veterinarian.html', {'vet': vet})


@login_required
@require_POST
def create_offer(request, pk):
    """
    Create price offer for an animal (Smart Offer)
    HTMX view that returns success message
    """
    animal = get_object_or_404(Animal, pk=pk)
    
    # Prevent owner from making offers on their own animals
    if animal.owner == request.user:
        return JsonResponse({
            'error': 'Вы не можете предложить цену на своё объявление'
        }, status=400)
    
    # Check if user already has a pending offer
    existing_offer = Offer.objects.filter(
        animal=animal,
        buyer=request.user,
        status='pending'
    ).first()
    
    if existing_offer:
        return JsonResponse({
            'error': 'У вас уже есть активное предложение для этого объявления'
        }, status=400)
    
    # Get price from form
    try:
        price = float(request.POST.get('price', 0))
        message = request.POST.get('message', '')
        
        if price <= 0:
            return JsonResponse({
                'error': 'Цена должна быть больше нуля'
            }, status=400)
        
        # Create offer
        offer = Offer.objects.create(
            animal=animal,
            buyer=request.user,
            price=price,
            message=message
        )
        
        # Send notification to owner (optional)
        try:
            from .utils import send_telegram_message
            send_telegram_message(
                f"💰 Новое предложение цены!\n"
                f"Объявление: {animal.title}\n"
                f"Предложение: {price} TJS\n"
                f"От: {request.user.username}"
            )
        except:
            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Ваше предложение отправлено владельцу!'
        })
        
    except ValueError:
        return JsonResponse({
            'error': 'Неверный формат цены'
        }, status=400)


@login_required
def get_animal_fields(request):
    """
    ЗАДАЧА 3: HTMX view для динамической загрузки полей в зависимости от категории животного
    Возвращает partial template с специфичными полями для выбранной категории
    """
    category = request.GET.get('category', '')
    
    context = {
        'category': category,
    }
    
    # Определяем какой partial template рендерить
    if category in ['cow', 'sheep', 'goat', 'horse']:
        # Для скота: вес, порода скота, пол
        template = 'core/partials/livestock_fields.html'
    elif category == 'pigeon':
        # Для голубей: порода голубя, стиль игры, длительность полета
        template = 'core/partials/pigeon_fields.html'
    elif category in ['cat', 'dog']:
        # Для питомцев: порода питомца, паспорт
        template = 'core/partials/pet_fields.html'
    elif category == 'transport':
        # Для транспорта: тип авто, маршрут
        template = 'core/partials/transport_fields.html'
    else:
        # Для остальных категорий: только базовые поля (возраст)
        template = 'core/partials/basic_fields.html'
    
    return render(request, template, context)
