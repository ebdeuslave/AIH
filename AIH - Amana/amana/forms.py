from django import forms
from .models import Livraison


class LivraisonForm(forms.ModelForm):
    class Meta:
        model = Livraison
        fields = '__all__'

class LivraisonAddForm(forms.ModelForm):
    class Meta:
        model = Livraison
        exclude = ('created','updated', 'status', 'cab')