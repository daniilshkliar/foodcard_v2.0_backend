from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from django_better_admin_arrayfield.models.fields import ArrayField

from core.models import Place
from accounts.models import User


class GeneralReview(models.Model):
    NOISE_CHOICES = [
        ("S", "Quiet"),
        ("M", "Moderate"),
        ("L", "Loud"),
    ]

    place = models.OneToOneField(Place, on_delete=models.CASCADE, primary_key=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, validators = [MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)
    rounded_rating = models.PositiveSmallIntegerField(validators = [MaxValueValidator(5)], null=True, blank=True)
    food = models.DecimalField(max_digits=2, decimal_places=1, validators = [MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)
    service = models.DecimalField(max_digits=2, decimal_places=1, validators = [MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)
    ambience = models.DecimalField(max_digits=2, decimal_places=1, validators = [MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)
    noise = models.CharField(max_length=1, choices=NOISE_CHOICES, null=True, blank=True)
    amount = models.PositiveIntegerField(default=0)
    distribution = ArrayField(models.PositiveIntegerField(), size=5, default=list([0]*5))

    def __str__(self):
        return f"{self.place.title}: {self.rating}"


class Review(models.Model):
    NOISE_CHOICES = [
        ("S", "Quiet"),
        ("M", "Moderate"),
        ("L", "Loud"),
    ]

    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=150)
    food = models.PositiveSmallIntegerField(validators = [MaxValueValidator(5)])
    service = models.PositiveSmallIntegerField(validators = [MaxValueValidator(5)])
    ambience = models.PositiveSmallIntegerField(validators = [MaxValueValidator(5)])
    noise = models.CharField(max_length=1, choices=NOISE_CHOICES)
    overall = models.PositiveSmallIntegerField(validators = [MaxValueValidator(5)], blank=True)
    review = models.CharField(max_length=2000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.place.title}: {self.user}"