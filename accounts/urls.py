from django.urls import path

from . import views


urlpatterns = [
    path('signup/', views.signup),
    path('activate/<uidb64>/<utoken>/', views.activate_account),
    path('login/', views.login),
    path('logout/', views.logout),
    path('refresh/', views.refresh),
    path('user/', views.UserViewSet.as_view({'get': 'retrieve'})),
    path('user/permissions/<int:pk>/', views.UserViewSet.as_view({'get': 'permissions'})),
]