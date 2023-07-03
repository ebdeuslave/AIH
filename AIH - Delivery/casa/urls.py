from django.urls import path
from .views import *
from datetime import date

fileN = f'Livraisons-{date.today()}'


app_name = 'livraison'


urlpatterns = [
    path('', index, name='index' ),
    path('developer/', developer, name='developer'),
    path('livraison/', livraison, name='livraison'),
    path('livraison/get', livraison),
    path('livraison/add_livraison/', add_livraison, name='add_livraison'),
    path('livraison/<int:id>/update', update_livraison, name="update_livraison"),
    path('livraison/<int:id>/delete', delete, name="delete_livraison"),
    path('livraison/search', search, name='search_results'),
    path('zones/', zones, name='zones'),  
    path('zones/add_zone/', add_zone, name='add_zone'),
    path('zones/<int:id>/update', update_zone, name="update_zone"),
    path('login', loginPage, name='login_page'),
    path('logout', logoutUser, name='logout_page'),
    path(f'livraison/generatePDF_all_filtered_{fileN}/', ViewPDF2.as_view(), name='pdf_cmnd2'),  
    path('charts/', chartsView, name='charts'),
    path('monthlycharts/', monthlyChartsView, name='monthlyCharts'),
    path('charts/get', chartsView),
    path('zoneschart/', zonesChart, name='zoneschart'),
    path('zoneschart/get', zonesChart),
    path('changestatus/', changeCMDState, name='changestatus'),


    
]
