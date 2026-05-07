import pandas as pd
from django.core.management.base import BaseCommand
from bus.models import Stop, Route, RouteStop


class Command(BaseCommand):
    help = 'Import stops and routes from ODS files'

    def handle(self, *args, **kwargs):
        self.import_stops()
        self.import_routes()

    def import_stops(self):
        self.stdout.write('Importing stops...')
        df = pd.read_excel('data/stops.ods', engine='odf')

        for _, row in df.iterrows():
            Stop.objects.update_or_create(
                stop_id=row['StopID'],
                defaults={
                    'name': row['Name'],
                    'alt_names': row['AltNames'] if pd.notna(row['AltNames']) else '',
                    'latitude': row['Latitude'],
                    'longitude': row['Longitude'],
                    'notes': row['Notes'] if pd.notna(row['Notes']) else '',
                }
            )
        self.stdout.write(self.style.SUCCESS('Stops imported successfully!'))

    def import_routes(self):
        self.stdout.write('Importing routes...')
        df = pd.read_excel('data/routes.ods', engine='odf')

        for _, row in df.iterrows():
            # Create or update route
            route, _ = Route.objects.update_or_create(
                route_id=row['RouteID'],
                defaults={
                    'route_number': row['RouteNumber'],
                    'route_name': row['RouteName'],
                    'yatayat_id': row['YatayatID'],
                    'yatayat_name': row['YatayatName'],
                    'vehicle_type': row['VehicleType'],
                    'color': row['Color'] if pd.notna(row['Color']) else '',
                }
            )

            # Get the stop
            try:
                stop = Stop.objects.get(stop_id=row['StopID'])
            except Stop.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"Stop {row['StopID']} not found, skipping..."
                ))
                continue

            # Create route stop
            RouteStop.objects.update_or_create(
                route=route,
                stop=stop,
                defaults={
                    'stop_sequence': row['StopSequence'],
                    'direction': row['Direction'],
                }
            )

        self.stdout.write(self.style.SUCCESS('Routes imported successfully!'))