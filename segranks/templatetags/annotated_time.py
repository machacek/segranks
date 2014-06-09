from django import template

register = template.Library()

@register.simple_tag
def annotated_time(project, user):
    return project.annotated_time(user)
