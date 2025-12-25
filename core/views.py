"""
Views for GolubBozor - Pigeon Marketplace
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, F, Sum, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from decimal import Decimal
from .models import Pigeon, Bid, Comment, UserProfile, Review, PigeonImage
from .forms import PigeonForm, RegisterForm, BidForm, CommentForm, ReviewForm
from .utils import send_telegram_message


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
    Increments view counter using sessions to prevent duplicate counts
    Supports auction system with bid history and Q&A comments
    """
    pigeon = get_object_or_404(Pigeon, pk=pk)
    
    # Increment views count with session tracking
    session_key = f'viewed_pigeon_{pk}'
    if session_key not in request.session:
        # Mark as viewed in this session
        request.session[session_key] = True
        # Increment views count atomically
        Pigeon.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
        # Refresh from database to get updated count
        pigeon.refresh_from_db()
    
    # Check if current user has favorited this pigeon
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = pigeon.favorites.filter(id=request.user.id).exists()
    
    # Auction system: get bids and check if auction ended
    bids = pigeon.bids.all()[:10]  # Top 10 bids
    
    # Check if auction ended and determine winner
    if pigeon.listing_type == 'auction' and pigeon.auction_end_date:
        if timezone.now() >= pigeon.auction_end_date and not pigeon.is_sold:
            highest_bid = pigeon.get_highest_bid()
            if highest_bid:
                pigeon.winner = highest_bid.user
                pigeon.is_sold = True
                pigeon.save()
    
    # Bid form for authenticated users
    bid_form = None
    if request.user.is_authenticated and pigeon.is_auction_active():
        if pigeon.owner != request.user:
            bid_form = BidForm(pigeon=pigeon)
    
    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.pigeon = pigeon
            comment.user = request.user
            comment.save()
            
            # Send Telegram notification to pigeon owner
            if hasattr(pigeon.owner, 'profile') and pigeon.owner.profile.telegram_chat_id:
                message = f"🔔 <b>Новый вопрос о вашем объявлении</b>\n\n"
                message += f"Объявление: <b>{pigeon.title}</b>\n"
                message += f"Вопрос от: {comment.user.username}\n\n"
                message += f"Текст: {comment.text[:200]}"
                send_telegram_message(pigeon.owner.profile.telegram_chat_id, message)
            
            messages.success(request, '✅ Ваш вопрос опубликован!')
            return redirect('pigeon_detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    # Get all comments for this pigeon
    comments = pigeon.comments.all()
    
    context = {
        'pigeon': pigeon,
        'is_favorited': is_favorited,
        'bids': bids,
        'bid_form': bid_form,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'core/detail.html', context)


@login_required
def add_pigeon(request):
    """
    View for adding a new pigeon listing
    Supports multiple image uploads (up to 5 images)
    Requires user to be logged in
    New listings require moderation (is_approved=False by default)
    For auction listings, payment receipt is required
    """
    if request.method == 'POST':
        form = PigeonForm(request.POST, request.FILES)
        if form.is_valid():
            # Get uploaded extra images (gallery)
            extra_images = request.FILES.getlist('extra_images')
            
            # Validate image count (gallery)
            if len(extra_images) > 5:
                messages.error(request, '❌ Можно загрузить максимум 5 дополнительных изображений.')
                return render(request, 'core/add_pigeon.html', {'form': form})
            
            # Note: Main 'image' field is required in model as cover/thumbnail
            # extra_images are optional gallery photos
            
            pigeon = form.save(commit=False)
            pigeon.owner = request.user
            pigeon.is_approved = False  # Requires moderation
            
            # For auctions, initialize current_price with start_price
            if pigeon.listing_type == 'auction' and pigeon.start_price:
                pigeon.current_price = pigeon.start_price
            
            pigeon.save()
            
            # Save multiple extra images (gallery)
            for index, image_file in enumerate(extra_images):
                PigeonImage.objects.create(
                    pigeon=pigeon,
                    image=image_file,
                    order=index
                )
            
            # Different messages for auction vs fixed price
            gallery_msg = f" + {len(extra_images)} в галерее" if extra_images else ""
            if pigeon.listing_type == 'auction':
                messages.success(request, f'✅ Аукцион создан!{gallery_msg} После проверки чека оплаты (3 TJS) он будет активирован.')
            else:
                messages.success(request, f'✅ Объявление создано!{gallery_msg} Оно появится на сайте после проверки администратором.')
            
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
    User Dashboard: My Listings & My Bids
    Shows user's pigeon listings and pigeons they've bid on with auction status
    """
    # User's own listings
    my_listings = Pigeon.objects.filter(owner=request.user).order_by('-created_at')
    
    # Pigeons where user has placed bids
    my_bid_pigeons = Pigeon.objects.filter(
        bids__user=request.user,
        listing_type='auction'
    ).distinct().order_by('-auction_end_date')
    
    # Enhance each pigeon with bid status
    my_bids_data = []
    for pigeon in my_bid_pigeons:
        highest_bid = pigeon.get_highest_bid()
        user_highest_bid = pigeon.bids.filter(user=request.user).order_by('-amount').first()
        
        # Determine if user is winning
        is_winning = False
        if highest_bid and user_highest_bid:
            is_winning = (highest_bid.id == user_highest_bid.id)
        
        # Check if auction ended
        auction_ended = not pigeon.is_auction_active()
        
        my_bids_data.append({
            'pigeon': pigeon,
            'my_bid': user_highest_bid.amount if user_highest_bid else 0,
            'current_price': pigeon.current_price or pigeon.start_price,
            'is_winning': is_winning,
            'auction_ended': auction_ended,
            'is_winner': auction_ended and is_winning,
        })
    
    context = {
        'my_listings': my_listings,
        'my_bids_data': my_bids_data,
        'listings_count': my_listings.count(),
        'bids_count': len(my_bids_data),
    }
    return render(request, 'core/my_pigeons.html', context)


@login_required
def favorites(request):
    """
    Display user's favorite pigeons
    """
    favorite_pigeons = Pigeon.objects.filter(
        favorites=request.user,
        is_approved=True
    ).order_by('-created_at')
    
    context = {
        'favorite_pigeons': favorite_pigeons,
        'favorites_count': favorite_pigeons.count(),
    }
    return render(request, 'core/favorites.html', context)


def seller_profile(request, username):
    """
    Public seller profile view
    Shows seller's information and their approved listings
    Includes rating/review system
    """
    from django.db.models import Avg
    
    seller = get_object_or_404(User, username=username)
    
    # Only show approved listings on public profile
    approved_pigeons = Pigeon.objects.filter(
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
        user_has_reviewed = Review.objects.filter(seller=seller, author=request.user).exists()
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
                review.author = request.user
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
        'pigeons': approved_pigeons,
        'pigeon_count': approved_pigeons.count(),
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
@require_POST
def place_bid(request, pk):
    """
    Place a bid on an auction pigeon
    Validates bid amount and auction status
    """
    pigeon = get_object_or_404(Pigeon, pk=pk)
    
    # Validation checks
    if pigeon.listing_type != 'auction':
        messages.error(request, 'Это не аукцион')
        return redirect('pigeon_detail', pk=pigeon.pk)
    
    if not pigeon.is_auction_active():
        messages.error(request, 'Аукцион завершён')
        return redirect('pigeon_detail', pk=pigeon.pk)
    
    if pigeon.owner == request.user:
        messages.error(request, 'Вы не можете делать ставки на свой голубь')
        return redirect('pigeon_detail', pk=pigeon.pk)
    
    if request.method == 'POST':
        form = BidForm(request.POST, pigeon=pigeon)
        if form.is_valid():
            # 1. Get previous highest bidder BEFORE creating new bid
            previous_highest_bid = pigeon.bids.order_by('-amount').first()
            previous_user = None
            if previous_highest_bid:
                previous_user = previous_highest_bid.user
            
            # 2. Create new bid
            bid = form.save(commit=False)
            bid.pigeon = pigeon
            bid.user = request.user
            bid.save()
            
            # 3. Update current price
            pigeon.current_price = bid.amount
            pigeon.save()
            
            print(f"--- НАЧАЛО ОТПРАВКИ ТЕЛЕГРАМ ---")
            
            # 4. Send Telegram notification to pigeon owner
            if hasattr(pigeon.owner, 'profile') and pigeon.owner.profile.telegram_chat_id:
                message = f"💰 <b>Новая ставка на ваш аукцион!</b>\n\n"
                message += f"Объявление: <b>{pigeon.title}</b>\n"
                message += f"Ставка: <b>{bid.amount} TJS</b>\n"
                message += f"От пользователя: {bid.user.username}"
                send_telegram_message(pigeon.owner.profile.telegram_chat_id, message)
                print(f"Сообщение владельцу ({pigeon.owner.username}) отправлено.")
            else:
                print(f"У владельца ({pigeon.owner.username}) нет Chat ID.")
            
            # 5. Notify previous highest bidder that they were outbid
            if previous_user and previous_user != request.user and previous_user != pigeon.owner:
                if hasattr(previous_user, 'profile') and previous_user.profile.telegram_chat_id:
                    message = f"⚠️ <b>Вас перебили на аукционе!</b>\n\n"
                    message += f"Объявление: <b>{pigeon.title}</b>\n"
                    message += f"Ваша ставка: {previous_highest_bid.amount} TJS\n"
                    message += f"Новая ставка: <b>{bid.amount} TJS</b>\n\n"
                    message += f"Сделайте новую ставку, чтобы остаться в игре!"
                    send_telegram_message(previous_user.profile.telegram_chat_id, message)
                    print(f"Сообщение проигравшему ({previous_user.username}) отправлено.")
                else:
                    print(f"У прошлого лидера ({previous_user.username}) нет Chat ID.")
            
            print(f"--- КОНЕЦ ОТПРАВКИ ---")
            
            messages.success(request, f'Ваша ставка {bid.amount} TJS принята!')
            return redirect('pigeon_detail', pk=pigeon.pk)
    
    return redirect('pigeon_detail', pk=pigeon.pk)


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


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """
    Custom Admin Dashboard - Command Center
    High-level analytics and recent activity for site owners
    """
    # ==================== STATISTICS ====================
    
    # Total counts
    total_users = User.objects.count()
    total_pigeons = Pigeon.objects.count()
    
    # Active auctions (listing_type='auction', not sold, not expired)
    active_auctions = Pigeon.objects.filter(
        listing_type='auction',
        is_approved=True,
        is_sold=False,
        auction_end_date__gt=timezone.now()
    ).count()
    
    # Pending payment approvals
    pending_approvals = Pigeon.objects.filter(
        listing_type='auction',
        is_paid=False,
        payment_receipt__isnull=False
    ).exclude(payment_receipt='').count()
    
    # Total revenue (paid auctions * 3 TJS per auction)
    paid_auctions_count = Pigeon.objects.filter(
        listing_type='auction',
        is_paid=True
    ).count()
    total_revenue = paid_auctions_count * 3
    
    # ==================== RECENT ACTIVITY ====================
    
    # Last 5 registered users
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Last 5 added pigeons
    recent_pigeons = Pigeon.objects.select_related('owner').order_by('-created_at')[:5]
    
    # Additional analytics
    approved_pigeons = Pigeon.objects.filter(is_approved=True).count()
    pending_pigeons = Pigeon.objects.filter(is_approved=False).count()
    vip_pigeons = Pigeon.objects.filter(is_vip=True).count()
    sold_pigeons = Pigeon.objects.filter(is_sold=True).count()
    
    context = {
        # Main statistics
        'total_users': total_users,
        'total_pigeons': total_pigeons,
        'active_auctions': active_auctions,
        'pending_approvals': pending_approvals,
        'total_revenue': total_revenue,
        
        # Additional stats
        'approved_pigeons': approved_pigeons,
        'pending_pigeons': pending_pigeons,
        'vip_pigeons': vip_pigeons,
        'sold_pigeons': sold_pigeons,
        
        # Recent activity
        'recent_users': recent_users,
        'recent_pigeons': recent_pigeons,
    }
    
    return render(request, 'core/custom_dashboard.html', context)


@staff_member_required
def manager_dashboard(request):
    """
    Manager Dashboard - Review pending auction payment receipts
    Only accessible to staff users
    """
    # Fetch all auctions with receipts pending approval
    pending_payments = Pigeon.objects.filter(
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
def approve_payment(request, pigeon_id):
    """
    Approve auction payment receipt
    Marks payment as approved and notifies user via Telegram
    """
    pigeon = get_object_or_404(Pigeon, pk=pigeon_id, listing_type='auction')
    
    # Mark as paid
    pigeon.is_paid = True
    pigeon.save()
    
    # Notify user via Telegram
    try:
        profile = UserProfile.objects.filter(user=pigeon.owner).first()
        if profile and profile.telegram_chat_id:
            message = (
                f"✅ *Оплата принята!*\n\n"
                f"Ваш аукцион по голубю *{pigeon.title}* успешно запущен.\n\n"
                f"Стартовая цена: `{pigeon.start_price} TJS`\n"
                f"Дата окончания: `{pigeon.auction_end_date.strftime('%d.%m.%Y %H:%M')}`\n\n"
                f"Удачных торгов! 🦅"
            )
            send_telegram_message(profile.telegram_chat_id, message)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
    
    messages.success(request, f'Оплата для аукциона "{pigeon.title}" одобрена!')
    return redirect('manager_dashboard')


@staff_member_required
@require_POST
def reject_payment(request, pigeon_id):
    """
    Reject auction payment receipt
    Deletes receipt file and notifies user via Telegram
    """
    pigeon = get_object_or_404(Pigeon, pk=pigeon_id, listing_type='auction')
    
    # Delete receipt file if exists
    if pigeon.payment_receipt:
        if os.path.isfile(pigeon.payment_receipt.path):
            os.remove(pigeon.payment_receipt.path)
        pigeon.payment_receipt = None
        pigeon.save()
    
    # Notify user via Telegram
    try:
        profile = UserProfile.objects.filter(user=pigeon.owner).first()
        if profile and profile.telegram_chat_id:
            message = (
                f"❌ *Оплата отклонена*\n\n"
                f"К сожалению, чек для аукциона *{pigeon.title}* был отклонен.\n\n"
                f"*Причина:* Чек нечитаем или сумма неверна.\n\n"
                f"Пожалуйста, загрузите новый чек оплаты через форму редактирования объявления.\n\n"
                f"Требуемая сумма: `3 TJS`\n"
                f"Номер для оплаты: `+992 888 788 181`"
            )
            send_telegram_message(profile.telegram_chat_id, message)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
    
    messages.warning(request, f'Оплата для аукциона "{pigeon.title}" отклонена. Пользователь уведомлен.')
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
    
    messages.success(
        request,
        f'🗑️ Отзыв от пользователя "{author_name}" удалён.'
    )
    
    return redirect('seller_profile', username=seller_username)


# =============================================================================
# 🔒 SECURITY: Custom Error Handlers for Production
# =============================================================================

def custom_404(request, exception):
    """
    Custom 404 Not Found page - Shows clean branded error instead of Django debug
    """
    return render(request, 'core/404.html', status=404)


def custom_500(request):
    """
    Custom 500 Server Error page - Hides sensitive stack traces from users
    """
    return render(request, 'core/500.html', status=500)

