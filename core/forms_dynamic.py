"""
Динамическая форма для создания объявлений с HTMX
"""
from django import forms
from .models import Animal


class DynamicAnimalForm(forms.ModelForm):
    """
    Форма создания объявления с динамическими полями в зависимости от категории
    """
    
    class Meta:
        model = Animal
        fields = [
            # Обязательные поля
            'category', 'title', 'description', 'price', 'city', 'main_photo',
            'phone', 'whatsapp_number', 'telegram_username',
            
            # Специфичные поля для голубей
            'pigeon_breed', 'flight_duration', 'game_style', 'gender_pigeon',
            
            # Специфичные поля для скота
            'weight', 'age', 'livestock_breed', 'gender_livestock',
            
            # Специфичные поля для питомцев
            'pet_breed', 'has_passport', 'gender',
            
            # Видео
            'video_url',
        ]
        
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-[#D4AF37] bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none text-lg font-semibold',
                'hx-get': '/load-category-fields/',
                'hx-target': '#specific-fields',
                'hx-trigger': 'change',
                'hx-indicator': '#loading-indicator'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'Например: Британская короткошерстная кошка'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'Подробное описание животного, его характер, особенности...',
                'rows': 5
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': '1000'
            }),
            'city': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': '+992900123456'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': '+992900123456'
            }),
            'telegram_username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'username (без @)'
            }),
            'main_photo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'accept': 'image/*'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'https://youtube.com/watch?v=...'
            }),
            
            # Специфичные виджеты
            'pigeon_breed': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'Например: Бойный, Статный'
            }),
            'flight_duration': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'Например: 2-3 часа'
            }),
            'game_style': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'Например: Столбовой бой'
            }),
            'gender_pigeon': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': '300',
                'step': '0.01'
            }),
            'age': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'Например: 2 года'
            }),
            'livestock_breed': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'Например: Гиссарская'
            }),
            'gender_livestock': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none'
            }),
            'pet_breed': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none',
                'placeholder': 'Например: Британская'
            }),
            'has_passport': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-[#D4AF37] bg-[#1E1E1E] border-gray-600 rounded focus:ring-[#D4AF37]'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-600 bg-[#1E1E1E] text-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none'
            }),
        }
    
    def clean(self):
        """
        Валидация специфичных полей в зависимости от категории
        """
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        
        # Валидация для голубей
        if category == 'pigeon':
            if not cleaned_data.get('pigeon_breed'):
                self.add_error('pigeon_breed', 'Укажите породу голубя')
            if not cleaned_data.get('gender_pigeon'):
                self.add_error('gender_pigeon', 'Укажите пол голубя')
        
        # Валидация для скота
        if category in ['cow', 'sheep', 'horse', 'goat']:
            if not cleaned_data.get('weight'):
                self.add_error('weight', 'Укажите вес животного')
            if not cleaned_data.get('livestock_breed'):
                self.add_error('livestock_breed', 'Укажите породу')
            if not cleaned_data.get('age'):
                self.add_error('age', 'Укажите возраст')
        
        # Валидация для питомцев
        if category in ['dog', 'cat']:
            if not cleaned_data.get('pet_breed'):
                self.add_error('pet_breed', 'Укажите породу питомца')
        
        return cleaned_data
