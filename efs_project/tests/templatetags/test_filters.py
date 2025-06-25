from django import template

register = template.Library()

@register.filter
def class_name(obj):
    """Возвращает имя класса объекта"""
    return obj.__class__.__name__ 