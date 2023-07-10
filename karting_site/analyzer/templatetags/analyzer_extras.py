from django import template

register = template.Library()

@register.filter(name="lookup")
def lookup(dictionarie, key):
    return dictionarie[key]