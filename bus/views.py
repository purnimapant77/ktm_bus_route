from django.shortcuts import render
from .models import Stop, Route, RouteStop


def home(request):
    stops = Stop.objects.all().order_by('name')
    return render(request, 'bus/home.html', {'stops': stops})


def search_route(request):
    results = []
    from_stop = None
    to_stop = None
    error = None

    if request.method == 'POST':
        from_stop_id = request.POST.get('from_stop')
        to_stop_id = request.POST.get('to_stop')

        try:
            from_stop = Stop.objects.get(id=from_stop_id)
            to_stop = Stop.objects.get(id=to_stop_id)

            if from_stop == to_stop:
                error = "Please select different stops!"
            else:
                # Find routes that contain both stops
                from_routes = RouteStop.objects.filter(stop=from_stop).values_list('route', flat=True)
                to_routes = RouteStop.objects.filter(stop=to_stop).values_list('route', flat=True)
                common_route_ids = set(from_routes) & set(to_routes)

                for route_id in common_route_ids:
                    from_seq = RouteStop.objects.get(route_id=route_id, stop=from_stop).stop_sequence
                    to_seq = RouteStop.objects.get(route_id=route_id, stop=to_stop).stop_sequence

                    if from_seq < to_seq:
                        route = Route.objects.get(id=route_id)
                        # Get all stops in between
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

                if not results:
                    error = "No direct bus found between these stops. Try nearby stops!"

        except Stop.DoesNotExist:
            error = "Invalid stop selected!"

    stops = Stop.objects.all().order_by('name')
    return render(request, 'bus/search.html', {
        'stops': stops,
        'results': results,
        'from_stop': from_stop,
        'to_stop': to_stop,
        'error': error,
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