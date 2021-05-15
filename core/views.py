from django.db.models import Q
from django.conf import settings
from pytz import country_names
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from guardian.shortcuts import get_objects_for_user

from .models import *
from .serializers import *
from .utils import get_thumbnail
from backend.permissions import *
from reservations.utils import get_valid_tables 


class StandardCardsPagination(PageNumberPagination):
    page_size = 18
    page_size_query_param = 'page_size'
    max_page_size = 180


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    pagination_class = StandardCardsPagination
    permission_classes = [ReadOnly|IsAdminUser|IsStaff]

    def list(self, request):
        categories = self.request.query_params.getlist('cat')
        cuisines = self.request.query_params.getlist('cui')
        services = self.request.query_params.getlist('ser')
        country = self.request.query_params.get('ctr')
        city = self.request.query_params.get('cty')
        search = self.request.query_params.get('search')
        
        if search:
            places = self.queryset.filter(title__icontains=search).distinct().order_by('title')
        else:
            places = self.queryset.filter(
                (Q(main_category__in=categories) | Q(additional_categories__in=categories)) &
                (Q(main_cuisine__in=cuisines) | Q(additional_cuisines__in=cuisines)) &  
                (Q(additional_services__in=services) | Q(additional_cuisines__isnull=True)),
                country__name__iexact=country,
                city__iexact=city,
                is_active=True,
            ).distinct().order_by('title')
        
        page = self.paginate_queryset(places)
        if page is not None:
            serializer = CardSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CardSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_list_for_panel(self, request):
        places = get_objects_for_user(request.user, 'core.view_place').order_by('title')

        page = self.paginate_queryset(places)
        if page is not None:
            serializer = PlacesForControlPanelSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PlacesForControlPanelSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, city=None, title=None):
        try:
            place = self.queryset.get(title__iexact=title, city__iexact=city, is_active=True)
            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def get_by_id(self, request, pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.view_place').get(id=pk)
            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # only after purchase the product, became a manager and then can create the place
        if request.user.has_perm('core.add_place'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': "You don't have permission to create a place"}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=pk)
            serializer = self.get_serializer(place, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to update the place"}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.delete_place').get(id=pk, is_active=True)
            place.is_active = False
            place.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to delete the place"}, status=status.HTTP_403_FORBIDDEN)


class ImageViewSet(viewsets.ModelViewSet):
    queryset = PlaceImage.objects.all()
    serializer_class = PlaceImageSerializer
    permission_classes = [ReadOnly|IsAdminUser|IsStaff]

    def list(self, request, pk=None):
        images = self.queryset.filter(place=pk).order_by('id')
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=pk)
            images = request.FILES.getlist('photos')

            if images is not None and isinstance(images, list):
                objs = (PlaceImage(place=place, image=image, thumbnail=get_thumbnail(image)) for image in images)
                PlaceImage.objects.bulk_create(objs)
            else:
                return Response({'message': 'You must provide any photos'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(self.queryset.filter(place=place), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to change the place"}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=pk)
            images = request.data.get('photos')

            if images is not None and isinstance(images, list):
                images = self.queryset.filter(id__in=images, place=place)
                if place.main_photo and images.filter(thumbnail__endswith=place.main_photo[7:]).exists():
                    place.main_photo = None
                    place.save()
                images.delete()
            else:
                return Response({'message': 'You must provide any photos'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(self.queryset.filter(place=place), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to change the place"}, status=status.HTTP_403_FORBIDDEN)

    def set_main(self, request, pk=None, main_id=None):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=pk)
            image = self.queryset.get(id=main_id, place=place)
            place.main_photo = image.thumbnail.url
            place.save()
            return Response(status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to change the place"}, status=status.HTTP_403_FORBIDDEN)
        except PlaceImage.DoesNotExist:
            return Response({'message': 'This image does not exist'}, status=status.HTTP_404_NOT_FOUND)


class FavoritesViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoritesSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        places = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def handle(self, request, pk=None):
        try:
            place = Place.objects.get(id=pk, is_active=True)
            favorite = self.queryset.get(user=request.user, place=place)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Place.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Favorite.DoesNotExist:
            favorite = Favorite(user=request.user, place=place)
            favorite.save()
            return Response(status=status.HTTP_201_CREATED)


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [ReadOnly|Filter|IsAdminUser|IsStaff]

    def list(self, request, pk=None):
        tables = self.queryset.filter(place=pk)

        # page = self.paginate_queryset(tables)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(tables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def filter(self, request, pk=None):
        if filters := request.data.get('filters'):
            try:
                place = Place.objects.get(id=pk, is_active=True)
                tables = get_valid_tables(place, filters)
                serializer = self.get_serializer(tables, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Place.DoesNotExist:
                return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                return Response({'message': 'This place does not work at the time'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=request.data.get('place'))
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to change the place"}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None, table_pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=pk)
            table = self.queryset.get(id=table_pk, place=place)
            serializer = self.get_serializer(table, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to change the place"}, status=status.HTTP_403_FORBIDDEN)
        except Table.DoesNotExist:
            return Response({'message': 'This table does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None, table_pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=pk)
            table = self.queryset.get(id=table_pk, place=place)
            table.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to change the place"}, status=status.HTTP_403_FORBIDDEN)
        except Table.DoesNotExist:
            return Response({'message': 'This table does not exist'}, status=status.HTTP_404_NOT_FOUND)


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [ReadOnly|IsAdminUser|IsStaff]

    def list(self, request, pk=None, category=None):
        dishes = self.queryset.filter(place=pk, category=category).order_by('title')
        serializer = self.get_serializer(dishes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=request.data.get('place'))
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to change the menu"}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None, dish_pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=pk)
            dish = self.queryset.get(id=dish_pk, place=place)
            serializer = self.get_serializer(dish, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to change the menu"}, status=status.HTTP_403_FORBIDDEN)
        except Menu.DoesNotExist:
            return Response({'message': 'This dish does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None, dish_pk=None):
        try:
            place = get_objects_for_user(request.user, 'core.change_place').get(id=pk)
            dish = self.queryset.get(id=dish_pk, place=place)
            dish.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to change the menu"}, status=status.HTTP_403_FORBIDDEN)
        except Table.DoesNotExist:
            return Response({'message': 'This dish does not exist'}, status=status.HTTP_404_NOT_FOUND)