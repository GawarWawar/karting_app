from django import template

register = template.Library()

@register.filter(name="lookup")
def lookup(dictionarie, key):
    try:
        return dictionarie[key]
    except KeyError:
        return None