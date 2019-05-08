from rest_framework import permissions
from internal.models import Link
import pdb

class IsLinkCreator(permissions.BasePermission):
    """
    Custom permission to only allow creators of the links to have write access
    for their own links
    """
    def has_object_permission(self, request, view, obj):
        # Super user can always access
        if request.user.is_superuser or request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.creator

class HasEventPermission(permissions.BasePermission):
    """
    Custom permission to only allow link creators to have read access to their
    link events. Create access is currently public.
    TODO: set up synchronous API key?
    # TODO: fix these permissions lol idk what I'm doing
    """
    def has_permission(self, request, view):
      return request.user.is_superuser or request.method == 'POST'

    def has_object_permission(self, request, view, obj):
        # Super user can always access
        if request.user.is_superuser:
            return True
        return request.method in permissions.SAFE_METHODS and request.user == obj.link.creator
