import django_filters
from django_filters import *
from .models import *


class LivraisonFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created', lookup_expr='gte', label='de ')  
    end_date = DateFilter(field_name='created', lookup_expr='lte', label='à ')  
      
    class Meta:
        model = Livraison
        fields = ['zone__livreur', 'status'] 
 





