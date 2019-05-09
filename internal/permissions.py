from rest_framework import permissions
import pdb

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners/creators of a resource
    to have appropriate access
    """

    def has_object_permission(self, request, view, obj):
        # Super user can always access
        if request.user.is_superuser:
            return True
        if view.basename == 'Links' and request.method in permissions.SAFE_METHODS:
            return True
        if view.basename == 'Links':
            owner = obj.creator
        elif view.basename == 'Preferences':
            owner = obj.user
        elif view.basename == 'Users':
            owner = obj
        return request.user == owner