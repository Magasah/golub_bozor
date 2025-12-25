"""
Forms for GolubBozor
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Pigeon, Bid, Comment, Review


class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget to support multiple file uploads"""
    allow_multiple_selected = True


class PigeonForm(forms.ModelForm):
    """
    Form for adding/editing pigeon listings
    Supports multiple image uploads (up to 5 images)
    Main 'image' field = Cover/Thumbnail, 'extra_images' = Gallery
    """
    # Add multiple images field (not in model, handled separately)
    extra_images = forms.FileField(
        required=False,
        label='Дополнительные фото (до 5 фото)',
        help_text='Галерея: выберите до 5 изображений голубя',
        widget=MultipleFileInput(attrs={
            'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
            'accept': 'image/*'
        })
    )
    
    listing_type = forms.ChoiceField(
        choices=[('fixed', 'Фиксированная цена (Бесплатно)'), ('auction', 'Аукцион (Стоимость: 3 сомони)')],
        widget=forms.RadioSelect(attrs={
            'class': 'listing-type-radio'
        }),
        initial='fixed',
        label='Тип размещения'
    )
    
    class Meta:
        model = Pigeon
        fields = ['title', 'breed', 'game_type', 'sex', 'city', 'price', 'description', 
                  'image', 'video_url', 'phone', 'whatsapp_number', 'telegram_username', 'is_vip',
                  'listing_type', 'start_price', 'auction_end_date', 'payment_receipt']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'placeholder': 'Например: Бойный голубь Тегеранский'
            }),
            'breed': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none'
            }),
            'game_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none'
            }),
            'sex': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none'
            }),
            'city': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'rows': 6,
                'placeholder': 'Подробное описание птицы, возраст, особенности...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'accept': 'image/*'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'placeholder': '+992 XX XXX XX XX'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'placeholder': '+992900123456'
            }),
            'telegram_username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'placeholder': 'username (без @)'
            }),
            'is_vip': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-[#D4AF37] bg-[#1E1E1E] border-gray-700 rounded focus:ring-[#D4AF37]'
            }),
            'start_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'placeholder': 'Начальная цена аукциона',
                'step': '0.01'
            }),
            'auction_end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none'
            }, format='%Y-%m-%dT%H:%M'),
            'payment_receipt': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'accept': 'image/*'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get('listing_type')
        start_price = cleaned_data.get('start_price')
        auction_end_date = cleaned_data.get('auction_end_date')
        payment_receipt = cleaned_data.get('payment_receipt')
        
        if listing_type == 'auction':
            if not start_price:
                self.add_error('start_price', 'Для аукциона необходимо указать начальную цену')
            if not auction_end_date:
                self.add_error('auction_end_date', 'Для аукциона необходимо указать дату окончания')
            elif auction_end_date <= timezone.now():
                self.add_error('auction_end_date', 'Дата окончания должна быть в будущем')
            if not payment_receipt and not self.instance.pk:  # Only require for new listings
                self.add_error('payment_receipt', 'Для активации аукциона необходимо загрузить чек оплаты')
        
        return cleaned_data
    
    def clean_extra_images(self):
        """
        Validate that no more than 5 extra images are uploaded
        """
        # This will be checked in the view since request.FILES.getlist is needed
        return self.cleaned_data.get('extra_images')


class RegisterForm(UserCreationForm):
    """
    User registration form
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
            'placeholder': 'Email'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'placeholder': 'Имя пользователя'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
            'placeholder': 'Подтвердите пароль'
        })


class BidForm(forms.ModelForm):
    """
    Form for placing auction bids
    """
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none',
                'placeholder': 'Введите вашу ставку',
                'step': '0.01',
                'min': '0.01'
            })
        }
        labels = {
            'amount': 'Ваша ставка (TJS)'
        }
    
    def __init__(self, *args, pigeon=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pigeon = pigeon
        
        if pigeon:
            # Минимальная ставка = текущая цена + 1 TJS или начальная цена
            min_bid = pigeon.current_price or pigeon.start_price
            if pigeon.current_price:
                min_bid = pigeon.current_price + 1
            
            self.fields['amount'].widget.attrs['min'] = str(min_bid)
            self.fields['amount'].help_text = f'Минимальная ставка: {min_bid} TJS'
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if not self.pigeon:
            raise forms.ValidationError('Ошибка: голубь не найден')
        
        # Проверка минимальной ставки
        min_bid = self.pigeon.current_price or self.pigeon.start_price
        if self.pigeon.current_price:
            min_bid = self.pigeon.current_price + 1
        
        if amount < min_bid:
            raise forms.ValidationError(
                f'Ваша ставка должна быть минимум {min_bid} TJS'
            )
        
        return amount
        

class CommentForm(forms.ModelForm):
    """
    Form for asking questions about a pigeon
    """
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none resize-none',
                'placeholder': 'Задайте вопрос о голубе...',
                'rows': 3
            })
        }
        labels = {
            'text': 'Ваш вопрос'
        }


class ReviewForm(forms.ModelForm):
    """
    Form for leaving reviews/ratings for sellers
    """
    # Список запрещённых слов (русский + таджикский)
    PROFANITY_LIST = [
        # Русский мат
        'мат', 'ебу', 'еб', 'ёб', 'сука', 'сук', 'пидор', 'пидар', 'пид0р', 'хуй', 'ху!', 'хyй',
        'пизд', 'пи!д', 'пи3д', 'блять', 'блядь', 'бля', 'еба', 'ебан', 'ибу', 'уеб', 'заеб',
        'хер', 'херн', 'мудак', 'мудил', 'гандон', 'говн', 'дерьм', 'срать', 'усра', 'говнюк',
        # Таджикский мат
        'гом', 'оча', 'очат', 'очачон', 'падар', 'ота', 'отата', 'кер', 'кир', 'кус', 'кун',
        'харом', 'лаънат', 'джахонам', 'ҷаҳаннам', 'кафтар', 'хук', 'шугол',
    ]
    
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'rating-radio'
            }),
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-[#1E1E1E] border border-gray-700 rounded-lg text-gray-200 focus:border-[#D4AF37] focus:outline-none resize-none',
                'placeholder': 'Расскажите о своём опыте покупки (необязательно)...',
                'rows': 4
            })
        }
        labels = {
            'rating': 'Ваша оценка',
            'text': 'Комментарий (необязательно)'
        }
    
    def clean_text(self):
        """Проверка текста на наличие матерных слов и XSS"""
        text = self.cleaned_data.get('text', '')
        
        if not text:
            return text
        
        # Защита от XSS - удаление HTML тегов
        import re
        if re.search(r'<[^>]*script|javascript:|onerror=|onclick=', text, re.IGNORECASE):
            raise forms.ValidationError('❌ Обнаружена попытка вставки вредоносного кода!')
        
        # Нормализация текста для проверки (убираем спецсимволы, цифры вместо букв)
        normalized = text.lower()
        normalized = normalized.replace('!', '').replace('*', '').replace('@', '')
        normalized = normalized.replace('0', 'о').replace('3', 'з').replace('6', 'б')
        normalized = normalized.replace('4', 'ч').replace('1', 'і').replace('$', 's')
        normalized = normalized.replace(' ', '').replace('.', '').replace(',', '')
        
        # Проверка на мат
        for word in self.PROFANITY_LIST:
            if word in normalized:
                raise forms.ValidationError(
                    '❌ Ваш комментарий содержит недопустимые выражения. '
                    'Пожалуйста, используйте уважительную лексику.'
                )
        
        return text
