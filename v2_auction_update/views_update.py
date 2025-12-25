# ДОБАВЬ ЭТО В core/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Pigeon, Bid
from .forms import BidForm

# НОВАЯ ФУНКЦИЯ - добавь в конец файла:
@login_required
def place_bid(request, pigeon_id):
    """Размещение ставки на аукцион"""
    pigeon = get_object_or_404(Pigeon, id=pigeon_id)
    
    # Проверки
    if pigeon.listing_type != 'auction':
        messages.error(request, 'Это не аукцион')
        return redirect('pigeon_detail', pigeon_id=pigeon.id)
    
    if not pigeon.is_auction_active():
        messages.error(request, 'Аукцион завершён')
        return redirect('pigeon_detail', pigeon_id=pigeon.id)
    
    if pigeon.user == request.user:
        messages.error(request, 'Вы не можете делать ставки на свой голубь')
        return redirect('pigeon_detail', pigeon_id=pigeon.id)
    
    if request.method == 'POST':
        form = BidForm(request.POST, pigeon=pigeon)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.pigeon = pigeon
            bid.user = request.user
            bid.save()
            
            # Обновляем текущую цену
            pigeon.current_price = bid.amount
            pigeon.save()
            
            messages.success(request, f'Ваша ставка {bid.amount} TJS принята!')
            return redirect('pigeon_detail', pigeon_id=pigeon.id)
    else:
        form = BidForm(pigeon=pigeon)
    
    context = {
        'pigeon': pigeon,
        'form': form
    }
    return render(request, 'core/bid_form.html', context)


# ОБНОВИ СУЩЕСТВУЮЩУЮ ФУНКЦИЮ pigeon_detail - добавь информацию об аукционе:
"""
def pigeon_detail(request, pigeon_id):
    pigeon = get_object_or_404(Pigeon, id=pigeon_id)
    
    # Получаем все ставки (для аукционов)
    bids = pigeon.bids.all()[:10]  # Топ-10 ставок
    
    # Проверяем, завершён ли аукцион
    if pigeon.listing_type == 'auction' and pigeon.auction_end_date:
        if timezone.now() >= pigeon.auction_end_date and not pigeon.is_sold:
            # Аукцион завершён, определяем победителя
            highest_bid = pigeon.get_highest_bid()
            if highest_bid:
                pigeon.winner = highest_bid.user
                pigeon.is_sold = True
                pigeon.save()
    
    # Форма для новой ставки
    bid_form = None
    if request.user.is_authenticated and pigeon.is_auction_active():
        if pigeon.user != request.user:
            bid_form = BidForm(pigeon=pigeon)
    
    context = {
        'pigeon': pigeon,
        'bids': bids,
        'bid_form': bid_form,
    }
    return render(request, 'core/detail.html', context)
"""
