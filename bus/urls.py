from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_route, name='search_route'),
    path('yatayat/', views.yatayat_routes, name='yatayat_routes'),
    path('map/', views.map_view, name='map_view'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('stops/', views.stops_list, name='stops_list'),
]