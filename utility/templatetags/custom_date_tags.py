from django import template
from datetime import timedelta

register = template.Library()

def datetime_obj_to_ist_str(value):
    ist_obj = value + timedelta(hours=5, minutes=30)
    return ist_obj.strftime("%a, %b %d, %Y %H:%M:%S")

register.filter("datetime_obj_to_ist_str", datetime_obj_to_ist_str)