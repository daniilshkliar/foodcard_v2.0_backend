from datetime import datetime, timedelta
from smtplib import SMTPAuthenticationError

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from guardian.shortcuts import get_objects_for_user

from .models import *
from .serializers import *
from backend.permissions import *
from core.models import Place, Table
from core.views import StandardCardsPagination


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = StandardCardsPagination
    permission_classes = [IsAuthenticated|AllowCreateAndConfirmAndCancel]

    def list_by_user(self, request):
        reservations = self.queryset.filter(user=request.user, is_active=True).order_by('date_time')
        serializer = ListByUserReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list_by_place(self, request, pk=None):
        try:
            date_time = self.request.query_params.get('date_time')
            date = datetime.strptime(date_time, '%Y-%m-%d')

            place = get_objects_for_user(request.user, 'core.view_place').get(id=pk)
            reservations = self.queryset.filter(place=place, is_active=True, date_time__date=date).order_by('date_time')

            page = self.paginate_queryset(reservations)
            if page is not None:
                serializer = ListByPlaceReservationSerializer(reservations, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = ListByPlaceReservationSerializer(reservations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response({'message': "You don't have permission to manage reservations"}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, pk=None, table_id=None):
        try:
            place = Place.objects.get(id=pk, is_active=True)
            table = Table.objects.get(id=table_id, place=place)

            request.data['place'] = place.id
            request.data['place_object'] = place
            request.data['table'] = table.id
            request.data['table_object'] = table
            if request.user:
                if request.user.has_perm('core.view_place', place):
                    if not request.data.get('manager'):
                        request.data['user'] = request.user.id
                else:
                    request.data['user'] = request.user.id

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            response = Response(status=status.HTTP_201_CREATED)
            response.set_cookie(key='reserve', value=serializer.data.get('id'), httponly=True, max_age=300)
            return response
        except Place.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Table.DoesNotExist:
            return Response({'message': 'This table does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def confirm(self, request):
        if pk := request.COOKIES.get('reserve'):
            try:
                reservation = self.queryset.get(
                    id=pk,
                    created_at__gt=datetime.now()-timedelta(minutes=5),
                    is_active=False
                )

                serializer = self.get_serializer(reservation, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                send_mail(
                    'Confirmation of reservation',
                    f"""
                    Your reservation in {reservation.place.title}, table №{reservation.table.number} 
                    at {reservation.date_time} for {reservation.guests} guests has been confirmed.
                    """,
                    settings.EMAIL_HOST_USER,
                    [request.data.get('email')],
                    fail_silently=False,
                )
                
                response = Response(serializer.data, status=status.HTTP_200_OK)
                response.delete_cookie('reserve')
                return response
            except Reservation.DoesNotExist:
                return Response({'message': 'This reservation does not exist'}, status=status.HTTP_404_NOT_FOUND)
            except SMTPAuthenticationError as exc:
                return Response({"message" : exc.smtp_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            reservation = self.queryset.get(id=pk, is_active=True)

            if reservation.user is request.user or request.user.has_perm('core.view_place', reservation.place):
                reservation.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            return Response({'message': "You don't have permission to delete this reservation"}, status=status.HTTP_403_FORBIDDEN)
        except Reservation.DoesNotExist:
            return Response({'message': 'This reservation does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def cancel(self, request):
        if pk := request.COOKIES.get('reserve'):
            try:
                reservation = self.queryset.get(id=pk, is_active=False)
                reservation.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Reservation.DoesNotExist:
                return Response({'message': 'This reservation does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)