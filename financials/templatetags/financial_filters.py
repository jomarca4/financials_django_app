from django import template

register = template.Library()

@register.filter(name='millions_format')
def millions_format(value):
    try:
        # Convert to float, divide by a million and format with thousand separators
        value = float(value) / 1000000
        return "{:,.0f}M".format(value)
    except (ValueError, TypeError):
        return value  # Return the original value if conversion fails