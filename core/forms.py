"""
Forms for ZooBozor - Animal Marketplace
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Animal, AnimalImage, Review, Comment, Bid, Veterinarian


# � МОБИЛЬНАЯ АДАПТИВНОСТЬ - CSS классы
MOBILE_INPUT_CLASS = 'w-full px-4 py-3 md:py-2 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500 text-base md:text-sm'
MOBILE_SELECT_CLASS = 'w-full px-4 py-3 md:py-2 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500 text-base md:text-sm'
MOBILE_BUTTON_CLASS = 'w-full md:w-auto px-6 py-3 md:py-2 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#C5A028] transition text-base md:text-sm touch-manipulation'

def validate_username_format(value):
    """
    Проверка формата username:
    - Латинские буквы, цифры, подчеркивание
    - Подчеркивание НЕ может быть в начале или конце
    - Должен начинаться с буквы
    """
    if not value[0].isalpha():
        raise ValidationError('Имя пользователя должно начинаться с буквы.')
    
    if value.startswith('_') or value.endswith('_'):
        raise ValidationError('Подчеркивание не может быть в начале или конце имени.')
    
    # Проверка на допустимые символы
    import re
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$', value):
        raise ValidationError('Используйте только латинские буквы, цифры и подчеркивание (посередине).')


def validate_password_not_simple(value):
    """
    Запрещает простые пароли
    """
    forbidden_passwords = ['123456', 'password', 'qwerty', '123456789', 'pass', 'admin']
    if value.lower() in forbidden_passwords:
        raise ValidationError('Этот пароль слишком простой. Выберите более надежный.')


def validate_password_not_username(password, username):
    """
    Проверяет, что пароль не содержит имя пользователя
    """
    if username.lower() in password.lower():
        raise ValidationError('Пароль не должен содержать ваше имя пользователя.')



class AnimalSearchForm(forms.Form):
    """
    Search and filter form for animals
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Поиск животного...'
        }),
        label='Поиск'
    )
    
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'Все категории')] + Animal.CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500'
        }),
        label='Категория'
    )
    
    city = forms.ChoiceField(
        required=False,
        choices=[('', 'Все города')] + Animal.CITY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500'
        }),
        label='Город'
    )
    
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'Любой пол')] + Animal.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500'
        }),
        label='Пол'
    )
    
    price_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'От'
        }),
        label='Цена от (TJS)'
    )
    
    price_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'До'
        }),
        label='Цена до (TJS)'
    )
    
    listing_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Все типы'), ('fixed', 'Фиксированная цена'), ('auction', 'Аукцион')],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500'
        }),
        label='Тип продажи'
    )


class AnimalForm(forms.ModelForm):
    """
    Form for creating/editing animal listings with VIP photo limits
    Динамическая форма с условными полями для разных категорий
    """
    
    # Дополнительные поля для транспорта/зоо-такси
    transport_type = forms.ChoiceField(
        required=False,
        choices=Animal.TRANSPORT_TYPE_CHOICES,
        label='Тип транспорта',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500'
        })
    )
    
    route_from = forms.CharField(
        required=False,
        label='Маршрут: откуда',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Например: Душанбе'
        })
    )
    
    route_to = forms.CharField(
        required=False,
        label='Маршрут: куда',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Например: Худжанд'
        })
    )
    
    class Meta:
        model = Animal
        fields = [
            'category', 'title', 'description', 'gender', 'age', 'breed',
            'price', 'is_negotiable', 'listing_type', 'start_price', 'auction_end_date', 'payment_receipt',
            'main_photo', 'video_url', 'city', 'phone', 'whatsapp_number', 'telegram_username',
            'is_vip', 'transport_type', 'route_from', 'route_to',
            'departure_time', 'available_days', 'cargo_capacity',
            'weight', 'gender_livestock', 'color_variety', 'health_status',
            'flight_duration', 'game_style', 'has_passport',
        ]
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'id': 'id_category',
                'hx-get': '/load-category-fields/',
                'hx-target': '#dynamic-fields',
                'hx-trigger': 'change'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Например: Британская короткошерстная кошка'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'rows': 5,
                'placeholder': 'Подробное описание животного, характер, особенности...'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500'
            }),
            'age': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Например: 2 года, 6 месяцев'
            }),
            'breed': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Порода (если есть)'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': '1000'
            }),
            'listing_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'id': 'id_listing_type',
                'onchange': 'toggleAuctionFields()'
            }),
            'start_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Начальная цена для аукциона',
                'id': 'id_start_price'
            }),
            'auction_end_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'type': 'datetime-local',
                'id': 'id_auction_end_date'
            }),
            'main_photo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'accept': 'image/*'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'city': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': '+992XXXXXXXXX'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': '+992XXXXXXXXX (необязательно)'
            }),
            'telegram_username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'username (без @)'
            }),
            'payment_receipt': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'accept': 'image/*'
            }),
            'is_vip': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-[#D4AF37] bg-gray-800 border-gray-600 rounded focus:ring-2 focus:ring-[#D4AF37]',
                'id': 'id_is_vip'
            }),
        }


class AnimalImageForm(forms.ModelForm):
    """Form for uploading additional images with VIP limit validation"""
    class Meta:
        model = AnimalImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, user=None, animal=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.animal = animal
    
    def clean_image(self):
        """Валидация загрузки фото с учетом VIP статуса"""
        image = self.cleaned_data.get('image')
        
        if not image:
            return image
        
        # Проверка размера файла (максимум 5MB)
        if image.size > 5 * 1024 * 1024:
            raise ValidationError('Размер файла не должен превышать 5MB')
        
        # Проверка количества фото
        if self.animal and self.user:
            current_photos_count = self.animal.images.count()
            max_photos = 6 if hasattr(self.user, 'profile') and self.user.profile.is_vip else 4
            
            if current_photos_count >= max_photos:
                if self.user.profile.is_vip:
                    raise ValidationError('Лимит фото превышен. VIP пользователи могут загрузить до 6 фото.')
                else:
                    raise ValidationError('Лимит фото превышен. Стандартные пользователи могут загрузить до 4 фото. Купите VIP для увеличения лимита.')
        
        return image


class BidForm(forms.ModelForm):
    """Form for placing bids on pigeon auctions"""
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-yellow-500 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Ваша ставка (TJS)',
                'min': '1'
            })
        }


class VeterinarianSearchForm(forms.Form):
    """Search form for veterinarians"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Поиск ветклиники или врача...'
        }),
        label='Поиск'
    )
    
    city = forms.ChoiceField(
        required=False,
        choices=[('', 'Все города')] + Animal.CITY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500'
        }),
        label='Город'
    )


class VeterinarianForm(forms.ModelForm):
    """Form for adding veterinarian/clinic"""
    class Meta:
        model = Veterinarian
        fields = ['name', 'photo', 'description', 'phone', 'whatsapp_number', 'city', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Название клиники или имя врача'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'rows': 5,
                'placeholder': 'Описание услуг, опыт работы, специализация...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': '+992XXXXXXXXX'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': '+992XXXXXXXXX (необязательно)'
            }),
            'city': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Полный адрес клиники'
            }),
        }


class ReviewForm(forms.ModelForm):
    """Form for leaving reviews with star rating"""
    
    RATING_CHOICES = [
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'rating-radio'
        }),
        label='Оценка',
        required=True
    )
    
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-700 bg-[#121212] text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] placeholder-gray-500',
            'rows': 4,
            'placeholder': 'Расскажите о своем опыте работы с этим продавцом...'
        }),
        label='Комментарий',
        required=False
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'text']


class CommentForm(forms.ModelForm):
    """Form for comments"""
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'rows': 3,
                'placeholder': 'Ваш комментарий...'
            })
        }


class UserRegistrationForm(UserCreationForm):
    """
    🔒 Улучшенная форма регистрации с продвинутой валидацией
    """
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Email'
        }),
        help_text='Потребуется для верификации аккаунта'
    )
    
    phone = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': '+992XXXXXXXXX'
        }),
        help_text='Ваш номер телефона для связи'
    )
    
    # 🆕 Обязательное согласие с условиями
    terms_confirmed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-yellow-500 bg-gray-800 border-gray-600 rounded focus:ring-yellow-500'
        }),
        label='Я согласен с правилами пользования сайтом',
        error_messages={
            'required': 'Вы должны принять условия для регистрации.'
        }
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2', 'terms_confirmed']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Имя пользователя'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Применяем валидатор к username
        self.fields['username'].validators.append(validate_username_format)
        self.fields['username'].help_text = 'Латинские буквы, цифры и _ (посередине). Начните с буквы.'
        
        # Применяем валидатор к паролю
        self.fields['password1'].validators.append(validate_password_not_simple)
        self.fields['password1'].help_text = 'Минимум 8 символов. Не используйте простые пароли.'
        
        # Обновляем виджеты паролей
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-gray-800 text-white focus:ring-2 focus:ring-yellow-500',
            'placeholder': 'Подтверждение пароля'
        })
    
    def clean_username(self):
        """Дополнительная проверка username"""
        username = self.cleaned_data.get('username')
        
        # Проверяем, не занят ли username
        if User.objects.filter(username=username).exists():
            raise ValidationError('Это имя пользователя уже занято.')
        
        return username
    
    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже зарегистрирован.')
        
        return email
    
    def clean(self):
        """Проверка пароля на соответствие username"""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password1 = cleaned_data.get('password1')
        
        if username and password1:
            # Проверяем, что пароль не содержит username
            if username.lower() in password1.lower():
                raise ValidationError({
                    'password1': 'Пароль не должен содержать ваше имя пользователя.'
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Сохранение с установкой is_active=False для email-верификации"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # 🔒 Пользователь неактивен до подтверждения email
        user.is_active = False
        
        if commit:
            user.save()
            # Создаем профиль с телефоном
            user.profile.phone = self.cleaned_data['phone']
            user.profile.save()
        
        return user
