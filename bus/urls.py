from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_route, name='search_route'),
    path('yatayat/', views.yatayat_routes, name='yatayat_routes'),
]