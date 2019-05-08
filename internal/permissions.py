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