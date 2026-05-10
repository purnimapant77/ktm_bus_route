from django.db import models

class Stop(models.Model):
    stop_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    alt_names = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    route_id = models.CharField(max_length=10, unique=True)
    route_number = models.IntegerField()
    route_name = models.CharField(max_length=200)
    yatayat_id = models.IntegerField()
    yatayat_name = models.CharField(max_length=200)
    vehicle_type = models.CharField(max_length=50)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.route_id} - {self.route_name}"


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_stops')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='stop_routes')
    stop_sequence = models.IntegerField()
    direction = models.CharField(max_length=20, default='forward')

    class Meta:
        ordering = ['stop_sequence']

    def __str__(self):
        return f"{self.route} - Stop {self.stop_sequence}: {self.stop}"
    
    
from django.contrib.auth.models import User

class FavoriteRoute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    from_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='favorite_from')
    to_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='favorite_to')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'from_stop', 'to_stop']

    def __str__(self):
        return f"{self.user.username}: {self.from_stop.name} → {self.to_stop.name}"
