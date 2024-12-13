from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Trừ `arg` từ `value`."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0  # Nếu không thể thực hiện phép trừ, trả về 0


@register.filter(name='add_class')
def add_class(value, arg):
    """
    Thêm class vào phần tử form.
    Ví dụ: {{ form.email|add_class:"form-control" }}
    """
    return value.as_widget(attrs={'class': arg})