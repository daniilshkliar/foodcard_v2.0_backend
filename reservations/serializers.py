from django.conf import settings
from rest_framework import serializers

from .models import *
from reservations.utils import get_valid_tables


class ListByUserReservationSerializer(serializers.ModelSerializer):
    place = serializers.SerializerMethodField()
    table = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ('id', 'place', 'table', 'date_time', 'guests')

    def get_place(self, obj):
        return f"{obj.place.timezone}-{obj.place.city}/{obj.place.title}/"

    def get_table(self, obj):
        return obj.table.number


class ListByPlaceReservationSerializer(serializers.ModelSerializer):
    table = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ('date_time', 'guests', 'table', 'name', 'email', 'phone', 'id', 'comment')

    def get_table(self, obj):
        return obj.table.number


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

    def create(self, validated_data):
        place = self.initial_data.get('place_object')
        table = self.initial_data.get('table_object')
        date_time = validated_data.get('date_time')
        guests = validated_data.get('guests')

        filters = {
            'date_time': date_time,
            'max_guests__gte': guests,
            'min_guests__lte': guests
        }

        try:
            tables = get_valid_tables(place, filters)
        except ValueError:
            raise serializers.ValidationError('This place does not work at the time')
        
        if not table in tables:
            raise serializers.ValidationError('This table is already reserved')

        reservation = Reservation(
            place=validated_data.get('place'),
            table=validated_data.get('table'),
            date_time=date_time,
            guests=guests,
            user=validated_data.get('user')
        )
        reservation.save()

        return reservation

    def update(self, instance, validated_data):
        name = validated_data.get('name')
        phone = validated_data.get('phone')
        comment = validated_data.get('comment')
        email = validated_data.get('email')

        if not name or not phone or not email:
            raise serializers.ValidationError('Name, phone and email are required')

        instance.name = name
        instance.phone = phone
        instance.comment = comment
        instance.email = email
        instance.is_active = True

        instance.save()
        return instance