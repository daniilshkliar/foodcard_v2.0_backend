import pytz
from datetime import datetime, timedelta

from django.db.models import Q

from .models import Reservation
from core.models import Place, Table


def validate_date_time(place, date_time):
    # check before closure?
    timezone = pytz.timezone(place.timezone)

    if not isinstance(date_time, datetime):
        date_time = datetime.strptime(date_time[:19], '%Y-%m-%dT%H:%M:%S')
        date_time = date_time.astimezone(tz=timezone)
    else:
        date_time = date_time.replace(tzinfo=pytz.utc).astimezone(tz=timezone)
    
    now = datetime.now(tz=timezone)
    yyyy = date_time.year
    mm = date_time.month
    dd = date_time.day
    today = date_time.weekday()
    yesterday = today - 1

    if not place.opening_hours[today][0] and not place.opening_hours[today][1]:
        return None, False

    if not place.opening_hours[yesterday][0] and not place.opening_hours[yesterday][1]:
        today_min = place.opening_hours[today][0].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
        today_max = place.opening_hours[today][1].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
        
        date_time_is_valid = (
            date_time >= now and (
            (today_min >= today_max and date_time >= today_min) or
            (date_time >= today_min and date_time < today_max))
        )
    else:
        today_min = place.opening_hours[today][0].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
        today_max = place.opening_hours[today][1].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
        yesterday_min = place.opening_hours[yesterday][0].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
        yesterday_max = place.opening_hours[yesterday][1].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
    
        date_time_is_valid = (
            date_time >= now and (
            (yesterday_min >= yesterday_max and date_time < yesterday_max) or
            (today_min >= today_max and date_time >= today_min) or
            (date_time >= today_min and date_time < today_max))
        )
    
    return date_time, date_time_is_valid


def get_valid_tables(place, filters, avg_hours_spent=2):
    if not isinstance(place, Place) or not filters:
        raise TypeError

    exclude_tables = []
    
    if date_time := filters.get('date_time'):
        date_time, date_time_is_valid = validate_date_time(place, date_time)
        
        if not date_time_is_valid:
            raise ValueError
        
        min_border = date_time - timedelta(hours=avg_hours_spent)
        max_border = date_time + timedelta(hours=avg_hours_spent)

        reservations = Reservation.objects.filter(
            Q(is_active=True) | Q(created_at__gte=datetime.now()-timedelta(minutes=5), is_active=False),
            place=place,
            date_time__gte=min_border,
            date_time__lte=max_border,
        )

        exclude_tables = [reservation.table.id for reservation in reservations]

    filters = {
        key: value
        for key, value in filters.items()
        if key in ['max_guests__gte', 'min_guests__lte', 'floor', 'deposit__isnull', 'is_vip'] and value is not None
    }
    filters['place'] = place.id
    
    tables = Table.objects.filter(**filters).exclude(id__in=exclude_tables)
    
    return tables