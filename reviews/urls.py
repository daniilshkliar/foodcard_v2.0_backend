from django.urls import path

from . import views


urlpatterns = [
    path('list/<int:pk>/', views.ReviewViewSet.as_view({'get': 'list'})),
    path('create/<int:pk>/', views.ReviewViewSet.as_view({'post': 'create'})),
    path('general_review/<int:pk>/', views.GeneralReviewViewSet.as_view({'get': 'retrieve'})),
]