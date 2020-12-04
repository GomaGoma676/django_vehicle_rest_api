from django.db import models
from django.contrib.auth.models import User


class Segment(models.Model):
    segment_name = models.CharField(max_length=100)

    def __str__(self):
        return self.segment_name


class Brand(models.Model):
    brand_name = models.CharField(max_length=100)

    def __str__(self):
        return self.brand_name


class Vehicle(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    vehicle_name = models.CharField(max_length=100)
    release_year = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    segment = models.ForeignKey(
        Segment,
        on_delete=models.CASCADE
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.vehicle_name

