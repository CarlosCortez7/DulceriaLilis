from django import forms
from .models import Tareas

class FormularioTarea(forms.ModelForm):
    class Meta:
        model = Tareas
        fields = ['titulo', 'descripcion', 'importante']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'importante': forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),
        }