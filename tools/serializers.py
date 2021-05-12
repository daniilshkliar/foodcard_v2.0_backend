from django.conf import settings
from rest_framework import serializers

from guardian.models import UserObjectPermission

from .models import *
from accounts.serializers import UserSerializer


class StaffSerializer(serializers.ModelSerializer):
    permission = serializers.SlugRelatedField(read_only=True, slug_field='codename')
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserObjectPermission
        fields = ('permission', 'user')