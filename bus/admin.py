from django.contrib import admin
from .models import Stop, Route, RouteStop


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ['stop_id', 'name', 'alt_names', 'latitude', 'longitude']
    search_fields = ['name', 'alt_names']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['route_id', 'route_name', 'yatayat_name', 'vehicle_type', 'color']
    search_fields = ['route_name', 'yatayat_name']


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ['route', 'stop', 'stop_sequence', 'direction']
    list_filter = ['route', 'direction']
