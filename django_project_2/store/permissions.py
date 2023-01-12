from rest_framework.permissions import BasePermission
from rest_framework import permissions

from store.models import Customer


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class FullModelDjangoPermissions(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

class ViewCustomerHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_history')

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        user_id = request.user.id
        if Customer.objects.filter(user_id=user_id).exists():
            return True
        return False