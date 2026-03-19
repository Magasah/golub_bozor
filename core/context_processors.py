"""
Context processors для глобальных переменных шаблонов
"""
from datetime import datetime, date
from django.utils import timezone


def get_holiday_theme(request):
    """
    Автоматически определяет текущий праздник и возвращает CSS класс темы
    
    Возвращает:
        dict: {'holiday_theme': str|None, 'holiday_name': str|None}
    """
    # Принудительно активируем Навруз для деплоя
    now = timezone.now().date()
    current_year = now.year
    force_navruz = True
    
    # Праздничные периоды (диапазоны дат)
    holidays = {
        'ramadan': {
            'start': date(2026, 2, 17),  # Рамадан 2026
            'end': date(2026, 3, 19),
            'class': 'theme-ramadan',
            'name': 'Рамадан',
            'emoji': '🌙'
        },
        'eid_ramadan': {
            'start': date(2026, 3, 19),  # Ид аль-Фитр
            'end': date(2026, 3, 21),
            'class': 'theme-eid',
            'name': 'Иди Рамазан',
            'emoji': '✨'
        },
        'navruz': {
            'start': date(current_year, 3, 21),  # Навруз (фиксированная дата)
            'end': date(current_year, 3, 24),
            'class': 'theme-navruz',
            'name': 'Навруз',
            'emoji': '🌸'
        },
        'newyear': {
            'start': date(current_year - 1 if now.month == 1 and now.day < 5 else current_year, 12, 25),
            'end': date(current_year if now.month == 1 else current_year + 1, 1, 5),
            'class': 'theme-newyear',
            'name': 'Новый Год',
            'emoji': '🎄'
        }
    }
    
    # Проверяем, попадает ли текущая дата в какой-либо праздничный период
    if force_navruz:
        navruz = holidays['navruz']
        return {
            'holiday_theme': navruz['class'],
            'holiday_name': navruz['name'],
            'holiday_emoji': navruz['emoji'],
            'is_holiday': True
        }
    for holiday_key, holiday_data in holidays.items():
        if holiday_data['start'] <= now <= holiday_data['end']:
            return {
                'holiday_theme': holiday_data['class'],
                'holiday_name': holiday_data['name'],
                'holiday_emoji': holiday_data['emoji'],
                'is_holiday': True
            }
    
    # Обычный день (без праздника)
    return {
        'holiday_theme': None,
        'holiday_name': None,
        'holiday_emoji': None,
        'is_holiday': False
    }


def site_context(request):
    """
    Дополнительный контекст для всего сайта
    """
    return {
        'site_name': 'ЗооБозор',
        'site_emoji': '🦁',
        'current_year': timezone.now().year,
    }
