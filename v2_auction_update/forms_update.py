# ДОБАВЬ ЭТО В core/forms.py

from django import forms
from .models import Pigeon, Bid
from django.utils import timezone

# Обнови существующую PigeonForm - добавь новые поля:
"""
class PigeonForm(forms.ModelForm):
    class Meta:
        model = Pigeon
        fields = [
            'title', 'description', 'price', 'age', 
            'image1', 'image2', 'image3',
            'listing_type', 'start_price', 'auction_end_date'  # НОВЫЕ ПОЛЯ
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'auction_end_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get('listing_type')
        start_price = cleaned_data.get('start_price')
        auction_end_date = cleaned_data.get('auction_end_date')
        
        if listing_type == 'auction':
            if not start_price:
                raise forms.ValidationError('Для аукциона нужна начальная цена')
            if not auction_end_date:
                raise forms.ValidationError('Для аукциона нужна дата окончания')
            if auction_end_date <= timezone.now():
                raise forms.ValidationError('Дата окончания должна быть в будущем')
        
        return cleaned_data
"""


# НОВАЯ ФОРМА - добавь в конец файла core/forms.py:
class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
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
