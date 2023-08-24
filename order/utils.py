from datetime import datetime
from django.utils import timezone

def get_current_datetime():
    return timezone.now()

def get_current_date():
    return timezone.now().date()

def get_current_time():
    return timezone.now().time()
