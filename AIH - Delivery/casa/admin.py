from django.contrib import admin
from .models import Livreur, Zone, Livraison, Status
from rangefilter.filters import DateRangeFilter
from import_export.admin import ExportActionMixin


admin.site.site_header = "AFRICA INTERNET HOLDING"
admin.site.site_title = "AFRICA INTERNET HOLDING"
admin.site.index_title = "ADMINISTRATION - LIVRAISON CASA"


class Livraison_admin(ExportActionMixin,admin.ModelAdmin):
    list_filter = (('created', DateRangeFilter),'zone__livreur', 'status')   
    list_display = [field.name for field in Livraison._meta.get_fields()]
    search_fields = ('zone__nom', 'montant_DH', 'phone', 'commentaire', 'n_commande')
    list_per_page = 100
    list_max_show_all = 500   

    
class Zone_admin(admin.ModelAdmin):
    list_filter = ('livreur',) 
    list_display = ['id', 'nom', 'livreur']
    search_fields = ('nom',)
    list_per_page = 100 
    list_max_show_all = 500    

admin.site.register(Livreur)
admin.site.register(Status)
admin.site.register(Zone, Zone_admin)
admin.site.register(Livraison, Livraison_admin)
