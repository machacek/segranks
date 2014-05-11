from django import template
import segranks.detokenizator

register = template.Library()

@register.filter
def detokenize(value, lang):
    return segranks.detokenizator.detokenize(value.split(' '), lang)

