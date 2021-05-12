from django.urls import path

from . import views


urlpatterns = [
    path('staff/list/<int:pk>/', views.StaffViewSet.as_view({'get': 'list'})),
    path('staff/create/<int:pk>/', views.StaffViewSet.as_view({'post': 'create'})),
    path('staff/delete/<int:pk>/', views.StaffViewSet.as_view({'post': 'destroy'})),
    path('staff/fire/<int:pk>/', views.StaffViewSet.as_view({'post': 'fire_staff'})),
]