from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Trừ `arg` từ `value`."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0  # Nếu không thể thực hiện phép trừ, trả về 0
