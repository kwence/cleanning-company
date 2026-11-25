from django import template

register = template.Library()


@register.filter
def dict_get(mapping, key):
    if not mapping:
        return None
    try:
        return mapping.get(key)
    except Exception:
        return None
