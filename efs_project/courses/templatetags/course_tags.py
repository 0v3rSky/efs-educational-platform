from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def divmod(value, arg):
    """Возвращает остаток от деления value на arg"""
    try:
        return int(value) % int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def sub(value, arg):
    """Вычитает arg из value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0