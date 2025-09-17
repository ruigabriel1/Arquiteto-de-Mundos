from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Permite acessar um item de dicionário com uma chave variável no template."""
    return dictionary.get(key)
