"""
Forms for GolubBozor
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pigeon


class PigeonForm(forms.ModelForm):
    """
    Form for adding/editing pigeon listings
    """
    class Meta:
        model = Pigeon
        fields = ['title', 'breed', 'game_type', 'sex', 'city', 'price', 'description', 
                  'image', 'video_url', 'phone', 'whatsapp_number', 'telegram_username', 'is_vip']
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
        }


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
