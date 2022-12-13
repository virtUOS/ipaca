from re import L
from django import template
import random

register = template.Library()

@register.filter
def shuffle(value):
    l = value[:]
    random.shuffle(l)
    return l

