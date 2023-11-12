from django import forms
from .models import Makanan

class FormMakanan(forms.ModelForm):
    class Meta:
        model = Makanan
        fields = '__all__'