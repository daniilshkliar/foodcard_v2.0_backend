from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *
from core.models import Place
from accounts.models import User
from guardian.models import UserObjectPermission
from guardian.shortcuts import get_objects_for_user, assign_perm, remove_perm

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


class StaffViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.manage_place').get(id=pk)

            perms = ('view_place', 'add_place', 'change_place', 'delete_place', 'manage_place')
            perms = Permission.objects.filter(codename__in=perms)
            
            users = UserObjectPermission.objects.filter(object_pk=place.id, permission_id__in=perms)

            serializer = StaffSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to manage the place"}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.manage_place').get(id=pk)            
            user = User.objects.get(id=request.data.get('user'))
            assign_perm(request.data.get('permission'), user, place)

            group = Group.objects.get(name='Staff') 
            group.user_set.add(user)

            return Response(status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to manage the place"}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({'message': "User with provided id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Permission.DoesNotExist:
            return Response({'message': "Provided permission does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'message': "You must provide a valid permission"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.manage_place').get(id=pk)            
            user = User.objects.get(id=request.data.get('user'))
            remove_perm(request.data.get('permission'), user, place)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to manage the place"}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({'message': "User with provided id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Permission.DoesNotExist:
            return Response({'message': "Provided permission does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, AttributeError):
            return Response({'message': "You must provide a valid permission"}, status=status.HTTP_400_BAD_REQUEST)

    def fire_staff(self, request, pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.manage_place').get(id=pk)            
            user = User.objects.get(id=request.data.get('user'))
            
            perms = ('view_place', 'add_place', 'change_place', 'delete_place', 'manage_place')
            for perm in perms:
                remove_perm(perm, user, place)
            
            group = Group.objects.get(name='Staff') 
            group.user_set.remove(user)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to manage the place"}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({'message': "User with provided id does not exist"}, status=status.HTTP_400_BAD_REQUEST)