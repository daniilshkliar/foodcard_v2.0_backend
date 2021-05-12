import os

from django.db import models
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from djmoney.models.fields import MoneyField
from phonenumber_field.modelfields import PhoneNumberField
from django_better_admin_arrayfield.models.fields import ArrayField

from accounts.models import User


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
        
    def __str__(self):
        return self.name


class Cuisine(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        
    def __str__(self):
        return self.name


class AdditionalService(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
        

class Place(models.Model):
    title = models.CharField(max_length=70)
    phone = PhoneNumberField()
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    coordinates = ArrayField(models.DecimalField(max_digits=9, decimal_places=6), size=2)

    floor = models.PositiveSmallIntegerField(default=1, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    opening_hours = ArrayField(ArrayField(models.DateTimeField(null=True), size=2, null=True), size=7, null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    main_category = models.ForeignKey(Category, related_name='main_category', on_delete=models.PROTECT, null=True, blank=True)
    additional_categories = models.ManyToManyField(Category, blank=True)
    main_cuisine = models.ForeignKey(Cuisine, related_name='main_cuisine', on_delete=models.PROTECT, null=True, blank=True)
    additional_cuisines = models.ManyToManyField(Cuisine, blank=True)
    additional_services = models.ManyToManyField(AdditionalService, blank=True)
    main_photo = models.URLField(null=True, blank=True)

    is_active = models.BooleanField(default=False)

    models.UniqueConstraint(
        name='phone_is_active',
        fields=['is_active', 'phone'],
        condition=models.Q(is_active=True)
    )

    class Meta:
        permissions = (
            ('manage_place', 'Manage place'),
        )

    def __str__(self):
        return f"{self.title}, {self.country}, {self.city}"


class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='place_images')
    thumbnail = models.ImageField(upload_to='place_images', null=True, blank=True)


class MenuImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='menu_images')
    thumbnail = models.ImageField(upload_to='menu_images', null=True, blank=True)


class Table(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()
    max_guests = models.PositiveSmallIntegerField(validators = [MinValueValidator(1)])
    min_guests = models.PositiveSmallIntegerField(default=1, validators = [MinValueValidator(1)])
    floor = models.PositiveSmallIntegerField(default=1, blank=True, validators = [MinValueValidator(1)])
    deposit = MoneyField(max_digits=10, decimal_places=2, default_currency='BYN', null=True, blank=True)
    is_vip = models.BooleanField(default=False, blank=True)
    image = models.ImageField(upload_to='table_images', null=True, blank=True)

    def __str__(self):
        return f"№ {self.number}, {self.place}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)


@receiver(models.signals.post_delete, sender=MenuImage)
@receiver(models.signals.post_delete, sender=PlaceImage)
def auto_delete_image_and_thumbnail_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
    
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)


@receiver(models.signals.post_delete, sender=Table)
def auto_delete_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)