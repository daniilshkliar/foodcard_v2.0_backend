from django.conf import settings
from rest_framework import serializers

from .models import *


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    def create(self, validated_data):
        review = Review(
            place=validated_data.get('place'),
            user=validated_data.get('user'),
            name=validated_data.get('name'),
            food=validated_data.get('food'),
            service=validated_data.get('service'),
            ambience=validated_data.get('ambience'),
            noise=validated_data.get('noise'),
            overall=round((validated_data.get('food') + validated_data.get('service') + validated_data.get('ambience'))/3),
            review=validated_data.get('review')
        )

        review.save()
        return review


class GeneralReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralReview
        fields = '__all__'