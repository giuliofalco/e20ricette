from django import template

register = template.Library()

@register.filter
def star_rating(rate):
    full_stars = "★" * rate
    empty_stars = "☆" * (5 - rate)
    return full_stars + empty_stars
