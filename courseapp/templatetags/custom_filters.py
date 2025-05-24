from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Splits a string by the specified separator."""
    return value.split(arg)

@register.filter
def trim(value):
    """Removes leading and trailing whitespace."""
    return value.strip()

@register.filter
def range_filter(value):
    return range(1, value + 1)

@register.filter
def custom_date_format(value):
    return value.strftime("%b %d, %Y")

@register.filter
def course_duration_round(days):
    number = days / 30.0

    # Get the integer and decimal parts
    integer_part = int(number)
    decimal_part = number - integer_part

    # Apply the rounding logic
    if 0 < decimal_part <= 0.49:
        return integer_part + 0.5
    elif 0.51 <= decimal_part < 1:
        return integer_part + 1
    else:
        return number
    

@register.filter
def subtract(value, arg):
    """Subtracts arg from value"""
    return value - arg