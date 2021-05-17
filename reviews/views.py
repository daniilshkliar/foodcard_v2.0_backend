from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *
from backend.permissions import *
from core.models import Place
from core.views import StandardCardsPagination


def update_general_review(generalreview, place_id):
    if not isinstance(generalreview, GeneralReview) or not place_id:
        raise TypeError
        
    new_general_review = Review.objects.raw(f"""WITH pre_select as (
            SELECT
                count(id) as id,
                count(id) as amount,
                sum(food) as food,
                sum(service) as service,
                sum(ambience) as ambience,
                count(noise) filter (where noise = 'S') as small,
                count(noise) filter (where noise = 'M') as moderate,
                count(noise) filter (where noise = 'L') as loud,
                count(overall) filter (where overall = 1) as star_1,
                count(overall) filter (where overall = 2) as star_2,
                count(overall) filter (where overall = 3) as star_3,
                count(overall) filter (where overall = 4) as star_4,
                count(overall) filter (where overall = 5) as star_5
            FROM public.reviews_review
            where place_id = {place_id}
            group by place_id)
        SELECT
            id,
            amount as amount,
            ROUND((food+service+ambience)/(3*amount)::numeric, 1) as rating,
            ROUND((food+service+ambience)/(3*amount)::numeric) as rounded_rating,
            ROUND((food::float/amount)::numeric, 1) as food,
            ROUND((service::float/amount)::numeric, 1) as service, 
            ROUND((ambience::float/amount)::numeric, 1) as ambience,
            array_agg(array[star_1,star_2,star_3,star_4,star_5]) as distribution,
            CASE
                WHEN small = moderate AND moderate = loud THEN 'M'
                WHEN small = loud THEN 'M'
                WHEN moderate >= small AND moderate >= loud THEN 'M'
                WHEN small >= moderate AND small >= loud THEN 'S'
                WHEN loud  >= moderate AND loud  >= small THEN 'L'
            END as noise
        from pre_select
        group by id, amount, rating, rounded_rating, food, service, ambience, small, moderate, loud;""")
	
    for info in new_general_review:
        generalreview.amount = info.amount
        generalreview.rating = info.rating
        generalreview.rounded_rating = info.rounded_rating
        generalreview.food = info.food
        generalreview.service = info.service
        generalreview.ambience = info.ambience
        generalreview.distribution = info.distribution[0]
        generalreview.noise = info.noise

        generalreview.save()

    return True


class GeneralReviewViewSet(viewsets.ModelViewSet):
    queryset = GeneralReview.objects.all()
    serializer_class = GeneralReviewSerializer
    permission_classes = [ReadOnly]

    def retrieve(self, request, pk=None):
        try:
            review = self.queryset.get(place=pk)
            serializer = self.get_serializer(review)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GeneralReview.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = StandardCardsPagination
    permission_classes = [ReadOnly|IsAuthenticated]

    def list(self, request, pk=None):
        reviews = self.queryset.filter(place=pk).order_by('-created_at')

        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        try:
            place = Place.objects.get(id=pk)
            request.data['place'] = place.id
            request.data['user'] = request.user.id

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            try:
                update_general_review(place.generalreview, place.id)
            except TypeError:
                print('place is not instance of Place')

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Place.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)