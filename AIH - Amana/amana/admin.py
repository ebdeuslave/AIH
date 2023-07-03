from django.contrib import admin

from amana.models import *

# Register your models here.

admin.site.register(Status)

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('cab', 'site', 'name','phone','city','status', 'created', 'updated')
    readonly_fields = ["created", "updated",]   
