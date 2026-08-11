from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def in_groups(user, group_names):
    names = [name.strip() for name in group_names.split(",")]
    return user.groups.filter(name__in=names).exists()

@register.filter
def is_superadmin_or_admin(user):
    return user.groups.filter(name__in=["Superadmin", "Admin"]).exists()
