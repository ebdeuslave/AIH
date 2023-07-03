from django.urls import path
from django.conf.urls import include, url
from .views import *
from datetime import date, datetime
from django.conf.urls.static import static
from django.conf import settings

fileN = f'Livraisons-Amana-{date.today()}'
app_name = 'amanaApp'

urlpatterns = [
    path('developer/', developer, name='developer'),
    path('', livraison, name='livraison'),
    path('get', livraison),
    path('add_livraison/', add_livraison, name='add_livraison'),
    path('<int:id>/update_livraison', update_livraison, name="update_livraison"),
    path('search', search, name='search_results'),
    path('login', loginPage, name='login_page'),
    path('logout', logoutUser, name='logout_page'),
    path(f'etiquettes_{fileN}/', Etiquette.as_view(), name='etiquette'),  
    path(f'bon_de_ramassage_{fileN}/', Ramassage.as_view(), name='ramassage'), 

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
