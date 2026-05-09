from django.shortcuts import render
from .models import Stop, Route, RouteStop
import json
import math

def calculate_distance(lat1, lng1, lat2, lng2):
    """Haversine formula - calculates real distance in km between two coordinates"""
    R = 6371  # Earth radius in km
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def calculate_fare(distance_km, is_student=False):
    """Calculate fare based on Bagmati Province fare slabs, rounded up to nearest 5"""
    if distance_km <= 5:
        base_fare = 24
    elif distance_km <= 10:
        base_fare = 33
    elif distance_km <= 15:
        base_fare = 39
    elif distance_km <= 20:
        base_fare = 44
    else:
        base_fare = 50

    if is_student:
        base_fare = base_fare * 0.55  # 45% discount

    # Round UP to nearest 5
    import math
    fare = math.ceil(base_fare / 5) * 5
    return fare

def home(request):
    stops = Stop.objects.all().order_by('name')
    return render(request, 'bus/home.html', {'stops': stops})


def search_route(request):
    results = []
    from_stop = None
    to_stop = None
    error = None
    map_data = None
    is_student = False

    if request.method == 'POST':
        from_stop_id = request.POST.get('from_stop')
        to_stop_id = request.POST.get('to_stop')
        is_student = request.POST.get('is_student') == 'yes'

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

                        # Calculate total distance stop by stop
                        stop_list = list(stops_in_between)
                        total_distance = 0
                        for i in range(len(stop_list) - 1):
                            s1 = stop_list[i].stop
                            s2 = stop_list[i+1].stop
                            total_distance += calculate_distance(
                                s1.latitude, s1.longitude,
                                s2.latitude, s2.longitude
                            )

                        # Calculate fares
                        regular_fare = calculate_fare(total_distance, is_student=False)
                        student_fare = calculate_fare(total_distance, is_student=True)
                        final_fare = student_fare if is_student else regular_fare

                        results.append({
                            'route': route,
                            'from_stop': from_stop,
                            'to_stop': to_stop,
                            'from_seq': from_seq,
                            'to_seq': to_seq,
                            'stops_in_between': stops_in_between,
                            'distance': round(total_distance, 2),
                            'regular_fare': regular_fare,
                            'student_fare': student_fare,
                            'final_fare': final_fare,
                            'is_student': is_student,
                        })

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
        'is_student': is_student,
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
    
def about_view(request):
    return render(request, 'bus/about.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # For now just show success message
        # Later we can add email sending
        from django.contrib import messages
        messages.success(request, f'Thank you {name}! Your message has been received. We will get back to you soon.')
        return redirect('contact')
    return render(request, 'bus/contact.html')

def stops_list(request):
    stops = Stop.objects.all().order_by('name')
    return render(request, 'bus/stops.html', {'stops': stops})