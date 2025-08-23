from django import forms
from .models import BeermatFormat

class BeermatForm(forms.ModelForm):
    class Meta:
        model = BeermatFormat
        fields = '__all__'