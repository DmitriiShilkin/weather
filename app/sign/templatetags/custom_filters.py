from django import template

register = template.Library()


@register.filter()
def get_user(value):
    try:
        list_ = value.split('/')
    except AttributeError:
        print('Ошибка! Неверный тип данных - должна быть строка!')
    else:
        return list_[-1]
