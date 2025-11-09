from django import template

register = template.Library()

@register.filter(name='attr')
def attr(field, attrs):
    """
    Añade atributos HTML a un campo de formulario de Django.
    
    Uso en el template:
    {{ form.mi_campo|attr:"class:clase-css,form:mi-form-id" }}
    """
    
    # Dividir el string de atributos (ej: "class:valor,id:valor")
    attr_list = attrs.split(',')
    attr_dict = {}
    
    for attr in attr_list:
        try:
            # Dividir cada par (ej: "class:valor")
            key, value = attr.split(':', 1)
            attr_dict[key.strip()] = value.strip()
        except ValueError:
            # Ignorar si el formato es incorrecto (ej. "clase-css")
            pass
    
    # <--- EDITADO: Inicio de la corrección
    # Verificamos si 'field' es un objeto de campo (que tiene 'as_widget')
    # o si es un simple string (que no lo tiene).
    if hasattr(field, 'as_widget'):
        # Si es un campo, devolvemos el widget con los atributos
        return field.as_widget(attrs=attr_dict)
    else:
        # Si es un string (o cualquier otra cosa), lo devolvemos tal cual.
        return field
    # <--- EDITADO: Fin de la corrección