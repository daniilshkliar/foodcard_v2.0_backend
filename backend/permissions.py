from rest_framework.permissions import BasePermission, SAFE_METHODS
# from django.contrib.auth.models import Group


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class AllowCreateAndConfirmAndCancel(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create' or view.action == 'confirm' or view.action == 'cancel':
            return True

        return False


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Staff').exists():
            return True

        return False


class Filter(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'filter':
            return True

        return False


# class IsAdminUserOrReadOnly(BasePermission):
#     """
#     The request is authenticated as an admin or manager.
#     """

#     def has_permission(self, request, view):
#         return bool(
#             request.method in SAFE_METHODS or
#             request.user and
#             request.user.is_staff
#         )


# class IsAdminUserOrManager(BasePermission):
#     """
#     The request is authenticated as an admin or manager.
#     """

#     def has_permission(self, request, view):
#         try:
#             manager = Manager.objects.get(user=request.user.id)
#             is_manager = bool(manager.places)
#         except:
#             is_manager = False
        
#         return bool(
#             request.user and
#             request.user.is_staff or
#             is_manager
#         )


# class ManagerUpdateOnly(BasePermission):
#     """
#     The request is authenticated as a manager for update.
#     """

#     def has_permission(self, request, view):
#         PATH = request.META.get('PATH_INFO').split('/')
#         try:
#             pk = PATH[-2]
#             manager = Manager.objects.get(user=request.user.id)
#             is_manager = pk in [str(place.id) for place in manager.places]
#         except:
#             is_manager = False
        
#         return bool(
#             request.user and
#             is_manager and
#             PATH[-3]=='update'
#         )


# class IsManagerOrReadOnly(BasePermission):
#     """
#     The request is authenticated as a manager, or is a read-only request.
#     """

#     def has_permission(self, request, view):
#         try:
#             pk = request.META.get('PATH_INFO').split('/')[-2]
#             manager = Manager.objects.get(user=request.user.id)
#             is_manager = pk in [str(place.id) for place in manager.places]
#         except:
#             is_manager = False

#         return bool(
#             request.method in SAFE_METHODS or
#             request.user and
#             is_manager
#         )