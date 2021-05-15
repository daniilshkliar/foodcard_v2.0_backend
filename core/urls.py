from django.urls import path

from . import views


urlpatterns = [
    path('places/get/<slug:city>/<slug:title>/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
    path('places/', views.PlaceViewSet.as_view({'get': 'list'})),
    path('places/create/', views.PlaceViewSet.as_view({'post': 'create'})),
    path('places/update/<int:pk>/', views.PlaceViewSet.as_view({'post': 'update'})),
    path('places/delete/<int:pk>/', views.PlaceViewSet.as_view({'post': 'destroy'})),
    path('images/place/get/<int:pk>/', views.ImageViewSet.as_view({'get': 'list'})),
    path('images/place/upload/<int:pk>/', views.ImageViewSet.as_view({'post': 'create'})),
    path('images/place/delete/<int:pk>/', views.ImageViewSet.as_view({'post': 'destroy'})),
    path('images/place/set_main/<int:pk>/<int:main_id>/', views.ImageViewSet.as_view({'post': 'set_main'})),
    path('favorites/', views.FavoritesViewSet.as_view({'get': 'list'})),
    path('favorites/handle/<int:pk>/', views.FavoritesViewSet.as_view({'post': 'handle'})),
    path('panel/places/', views.PlaceViewSet.as_view({'post': 'get_list_for_panel'})),
    path('panel/places/get/<int:pk>/', views.PlaceViewSet.as_view({'post': 'get_by_id'})),
    path('tables/<int:pk>/', views.TableViewSet.as_view({'get': 'list'})),
    path('tables/filter/<int:pk>/', views.TableViewSet.as_view({'post': 'filter'})),
    path('tables/create/', views.TableViewSet.as_view({'post': 'create'})),
    path('tables/update/<int:pk>/<int:table_pk>/', views.TableViewSet.as_view({'post': 'update'})),
    path('tables/delete/<int:pk>/<int:table_pk>/', views.TableViewSet.as_view({'post': 'destroy'})),
    path('dishes/<int:pk>/<str:category>/', views.MenuViewSet.as_view({'get': 'list'})),
    path('dishes/create/', views.MenuViewSet.as_view({'post': 'create'})),
    path('dishes/update/<int:pk>/<int:dish_pk>/', views.MenuViewSet.as_view({'post': 'update'})),
    path('dishes/delete/<int:pk>/<int:dish_pk>/', views.MenuViewSet.as_view({'post': 'destroy'})),
]