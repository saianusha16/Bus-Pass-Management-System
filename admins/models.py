from django.db import models

class Route(models.Model):
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    distance = models.DecimalField(max_digits=6, decimal_places=2)  # in kilometers
    fare = models.DecimalField(max_digits=6, decimal_places=2)  # fare amount in currency (e.g., INR)

    def __str__(self):
        return f'{self.start_point} to {self.end_point} - {self.fare} INR'
