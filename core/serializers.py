import os
from decimal import Decimal

from django.conf import settings
from rest_framework import serializers
from django.db.utils import IntegrityError

from djmoney.money import Money
from timezonefinder import TimezoneFinder

from .models import *
from .utils import get_thumbnail
from reviews.models import GeneralReview


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'
        depth = 2

    def validate_title(self, value):
        return value.capitalize()

    def validate_city(self, value):
        return value.capitalize()
        
    def validate_opening_hours(self, value):
        if len(value) != 7:
            raise serializers.ValidationError('Opening hours must be quoted for all weekdays')

        for day in value:
            if len(day) != 2:
                raise serializers.ValidationError('Opening hours must be quoted for opening and closing')
        
        return value

    def validate_coordinates(self, value):
        if len(value) != 2:
            raise serializers.ValidationError('Must be quoted 2 coordinates')
        
        if not isinstance(value[0], Decimal) or not isinstance(value[1], Decimal):
            raise serializers.ValidationError('Coordinates must be decimal')

        return value

    def validate(self, data):
        if country := self.initial_data.get('country'):
            try:
                data['country'] = Country.objects.get(name=country)
            except Country.DoesNotExist:
                raise serializers.ValidationError(f'This country is not supported')

        for main_field, additional_field, model in (('main_category', 'additional_categories', Category), ('main_cuisine', 'additional_cuisines', Cuisine)):
            main = self.initial_data.get(main_field)
            additional = self.initial_data.get(additional_field)
            if main and isinstance(main, str) and isinstance(additional, list):
                try:
                    additional = set(additional)
                    additional.discard(main)
                    if len(additional) > 4:
                        raise serializers.ValidationError(f'Сan be selected maximum 4 {additional_field}')
                    
                    data[main_field] = model.objects.get(name=main)
                    data[additional_field] = model.objects.filter(name__in=additional)
                except model.DoesNotExist:
                    raise serializers.ValidationError(f'This {main_field} is not supported')
        
        additional_services = self.initial_data.get('additional_services')
        if isinstance(additional_services, list):
            try:
                additional_services = set(additional_services)
                if len(additional_services) > 10:
                    raise serializers.ValidationError(f'Сan be selected maximum 4 additional services')
                
                data['additional_services'] = AdditionalService.objects.filter(name__in=additional_services)
            except AdditionalService.DoesNotExist:
                raise serializers.ValidationError(f'This additional service is not supported')

        return data

    def create(self, validated_data):
        if not validated_data.get('country'):
            raise serializers.ValidationError(f'Country field is required')

        place = Place()
        place.title = validated_data.get('title')
        place.phone = validated_data.get('phone')
        place.country = validated_data.get('country')
        place.city = validated_data.get('city')
        place.street = validated_data.get('street')
        latitude, longitude = validated_data.get('coordinates')
        place.coordinates = [latitude, longitude]
        place.timezone = TimezoneFinder().timezone_at(lat=latitude, lng=longitude)
        place.is_active = True
        latitude, longitude = validated_data.get('coordinates')
        place.main_category = validated_data.get('main_category')
        place.main_cuisine = validated_data.get('main_cuisine')

        place.save()

        review = GeneralReview(place=place)
        review.save()

        return place

    def update(self, instance, validated_data):
        latitude, longitude = validated_data.get('coordinates', (None, None))
        if latitude and longitude:
            instance.country = validated_data.get('country', instance.country)
            instance.city = validated_data.get('city', instance.city)
            instance.street = validated_data.get('street', instance.street)
            instance.floor = validated_data.get('floor', instance.floor)
            instance.coordinates = [latitude, longitude]
            instance.timezone = TimezoneFinder().timezone_at(lat=latitude, lng=longitude)
        
        instance.title = validated_data.get('title', instance.title)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.description = validated_data.get('description', instance.description)
        instance.opening_hours = validated_data.get('opening_hours', instance.opening_hours)
        instance.instagram = validated_data.get('instagram', instance.instagram)
        instance.website = validated_data.get('website', instance.website)
        
        main = validated_data.get('main_category')
        additional = validated_data.get('additional_categories')
        if main and additional is not None:
            try:
                instance.additional_categories.set(additional)
                instance.main_category = main
            except (IntegrityError, ValueError):
                raise serializers.ValidationError(f'There are no such additional categories')

        main = validated_data.get('main_cuisine')
        additional = validated_data.get('additional_cuisines')
        if main and additional is not None:
            try:
                instance.additional_cuisines.set(additional)
                instance.main_cuisine = main
            except (IntegrityError, ValueError):
                raise serializers.ValidationError(f'There are no such additional categories')

        if additional := validated_data.get('additional_services'):
            try:
                instance.additional_services.set(additional)
            except (IntegrityError, ValueError):
                raise serializers.ValidationError(f'There are no such additional services')

        instance.save()
        return instance


class CardSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()
    rounded_rating = serializers.SerializerMethodField()

    class Meta:
        model = Place
        exclude = (
            'is_active',
            'phone',
            'floor',
            'description',
            'instagram',
            'website',
            'additional_categories',
            'additional_cuisines',
            'additional_services'
        )
        depth = 2

    def get_amount(self, obj):
        return obj.generalreview.amount
    
    def get_rounded_rating(self, obj):
        return obj.generalreview.rounded_rating


class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = '__all__'


class FavoritesSerializer(serializers.ModelSerializer):
    place = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ('place',)

    def get_place(self, obj):
        return f'{obj.place.city}/{obj.place.title}/'


class PlacesForControlPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('id', 'title', 'country', 'city', 'street', 'main_photo', 'is_active',)
        depth = 2


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

    def validate(self, data):
        if deposit := data.get('deposit'):
            data['deposit'] = Money(deposit, 'BYN')
        
        if image := data.get('image'):
            data['image'] = get_thumbnail(image)

        return data

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.max_guests = validated_data.get('max_guests', instance.max_guests)
        instance.min_guests = validated_data.get('min_guests', instance.min_guests)
        instance.floor = validated_data.get('floor', instance.floor)
        instance.deposit = validated_data.get('deposit', instance.deposit)
        instance.is_vip = validated_data.get('is_vip', instance.is_vip)

        image = validated_data.get('image')
        delete_image = self.initial_data.get('delete_image')
        if image and not delete_image:
            if instance.image:
                if os.path.isfile(instance.image.path):
                    os.remove(instance.image.path)
                    
            instance.image = image
        elif not image and delete_image:
            if instance.image:
                if os.path.isfile(instance.image.path):
                    os.remove(instance.image.path)
                
            instance.image.delete()

        instance.save()
        return instance


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

    def validate(self, data):
        if price := data.get('price'):
            data['price'] = Money(price, 'BYN')
        
        if image := data.get('image'):
            data['image'] = get_thumbnail(image, (500, 300))

        return data

    def update(self, instance, validated_data):
        instance.category = validated_data.get('category', instance.category)
        instance.title = validated_data.get('title', instance.title)
        instance.price = validated_data.get('price', instance.price)
        instance.composition = validated_data.get('composition', instance.composition)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.proteins = validated_data.get('proteins', instance.proteins)
        instance.fats = validated_data.get('fats', instance.fats)
        instance.carbohydrates = validated_data.get('carbohydrates', instance.carbohydrates)
        instance.calories = validated_data.get('calories', instance.calories)

        image = validated_data.get('image')
        delete_image = self.initial_data.get('delete_image')
        if image and not delete_image:
            if instance.image:
                if os.path.isfile(instance.image.path):
                    os.remove(instance.image.path)
                    
            instance.image = image
        elif not image and delete_image:
            if instance.image:
                if os.path.isfile(instance.image.path):
                    os.remove(instance.image.path)
                
            instance.image.delete()

        instance.save()
        return instance