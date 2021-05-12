from django.urls import path

from . import views


urlpatterns = [
    path('list_by_user/', views.ReservationViewSet.as_view({'get': 'list_by_user'})),
    path('list_by_place/<int:pk>/', views.ReservationViewSet.as_view({'get': 'list_by_place'})),
    path('create/<int:pk>/<int:table_id>/', views.ReservationViewSet.as_view({'post': 'create'})),
    path('confirm/', views.ReservationViewSet.as_view({'post': 'confirm'})),
    path('delete/<int:pk>/', views.ReservationViewSet.as_view({'post': 'destroy'})),
    path('cancel/', views.ReservationViewSet.as_view({'post': 'cancel'})),
]