from django import forms
from .models import *



class LivraisonForm(forms.ModelForm):
    class Meta:
        model = Livraison
        fields = '__all__'

class LivraisonAddForm(forms.ModelForm):
    class Meta:
        model = Livraison
        exclude = ('created', 'status')
        
        
class LivraisonEditForm(forms.ModelForm):
    class Meta:
        model = Livraison
        exclude = ('created', 'status', 'montant_DH',)


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = '__all__'
