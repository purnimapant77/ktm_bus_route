from django.shortcuts import render
from .models import Stop, Route, RouteStop
import json

def home(request):
    stops = Stop.objects.all().order_by('name')
    return render(request, 'bus/home.html', {'stops': stops})


def search_route(request):
    results = []
    from_stop = None
    to_stop = None
    error = None
    map_data = None

    if request.method == 'POST':
        from_stop_id = request.POST.get('from_stop')
        to_stop_id = request.POST.get('to_stop')

        try:
            from_stop = Stop.objects.get(id=from_stop_id)
            to_stop = Stop.objects.get(id=to_stop_id)

            if from_stop == to_stop:
                error = "Please select different stops!"
            else:
                from_routes = RouteStop.objects.filter(stop=from_stop).values_list('route', flat=True)
                to_routes = RouteStop.objects.filter(stop=to_stop).values_list('route', flat=True)
                common_route_ids = set(from_routes) & set(to_routes)

                map_routes = []
                map_stops = []
                added_stop_ids = set()

                for route_id in common_route_ids:
                    from_seq = RouteStop.objects.get(route_id=route_id, stop=from_stop).stop_sequence
                    to_seq = RouteStop.objects.get(route_id=route_id, stop=to_stop).stop_sequence

                    if from_seq < to_seq:
                        route = Route.objects.get(id=route_id)
                        stops_in_between = RouteStop.objects.filter(
                            route=route,
                            stop_sequence__gte=from_seq,
                            stop_sequence__lte=to_seq
                        ).order_by('stop_sequence')

                        results.append({
                            'route': route,
                            'from_stop': from_stop,
                            'to_stop': to_stop,
                            'from_seq': from_seq,
                            'to_seq': to_seq,
                            'stops_in_between': stops_in_between,
                        })

                        # Build map coordinates for this route segment
                        coords = []
                        for rs in stops_in_between:
                            coords.append([rs.stop.latitude, rs.stop.longitude])
                            if rs.stop.id not in added_stop_ids:
                                added_stop_ids.add(rs.stop.id)
                                map_stops.append({
                                    'name': rs.stop.name,
                                    'lat': rs.stop.latitude,
                                    'lng': rs.stop.longitude,
                                    'is_from': rs.stop.id == from_stop.id,
                                    'is_to': rs.stop.id == to_stop.id,
                                })

                        map_routes.append({
                            'route_id': route.route_id,
                            'route_name': route.route_name,
                            'yatayat_name': route.yatayat_name,
                            'color': route.color if route.color else 'blue',
                            'coordinates': coords,
                        })

                if not results:
                    error = "No direct bus found between these stops. Try nearby stops!"
                else:
                    map_data = json.dumps({
                        'stops': map_stops,
                        'routes': map_routes,
                        'from_stop': {'name': from_stop.name, 'lat': from_stop.latitude, 'lng': from_stop.longitude},
                        'to_stop': {'name': to_stop.name, 'lat': to_stop.latitude, 'lng': to_stop.longitude},
                    })

        except Stop.DoesNotExist:
            error = "Invalid stop selected!"

    stops = Stop.objects.all().order_by('name')
    return render(request, 'bus/search.html', {
        'stops': stops,
        'results': results,
        'from_stop': from_stop,
        'to_stop': to_stop,
        'error': error,
        'map_data': map_data,
    })


def yatayat_routes(request):
    routes = Route.objects.all().order_by('yatayat_name')
    selected_route = None
    route_stops = []

    route_id = request.GET.get('route')
    if route_id:
        try:
            selected_route = Route.objects.get(id=route_id)
            route_stops = RouteStop.objects.filter(
                route=selected_route
            ).order_by('stop_sequence')
        except Route.DoesNotExist:
            pass

    return render(request, 'bus/yatayat.html', {
        'routes': routes,
        'selected_route': selected_route,
        'route_stops': route_stops,
    })
    
def map_view(request):
    stops = Stop.objects.all()
    routes = Route.objects.all()

    # Prepare stops data for JavaScript
    stops_data = []
    for stop in stops:
        stops_data.append({
            'id': stop.id,
            'name': stop.name,
            'lat': stop.latitude,
            'lng': stop.longitude,
        })

    # Prepare routes data for JavaScript
    routes_data = []
    for route in routes:
        route_stops = RouteStop.objects.filter(
            route=route
        ).order_by('stop_sequence')
        
        coordinates = []
        for rs in route_stops:
            coordinates.append([rs.stop.latitude, rs.stop.longitude])
        
        routes_data.append({
            'route_id': route.route_id,
            'route_name': route.route_name,
            'yatayat_name': route.yatayat_name,
            'color': route.color if route.color else 'blue',
            'coordinates': coordinates,
        })

    return render(request, 'bus/map.html', {
        'stops_json': json.dumps(stops_data),
        'routes_json': json.dumps(routes_data),
    })