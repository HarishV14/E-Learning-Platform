from django import template
register = template.Library()

#model name template filter to get model name for an object
@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None