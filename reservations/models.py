from django.db import models
from django.core.validators import MinValueValidator

from phonenumber_field.modelfields import PhoneNumberField

from accounts.models import User
from core.models import Place, Table


class Reservation(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True)
    date_time = models.DateTimeField()
    guests = models.PositiveSmallIntegerField(validators = [MinValueValidator(1)])
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = PhoneNumberField(null=True, blank=True)
    comment = models.CharField(max_length=500, null=True, blank=True)
    reserved_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date_time} table {self.table}"