from rest_framework import permissions
from internal.models import User, Link
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

        # Links allows public read access
        if view.basename == 'Links' and request.method in permissions.SAFE_METHODS:
            return True

        # Events allows read access for objects owners only
        if view.basename == 'Events' and request.method in permissions.SAFE_METHODS and request.user == obj.link.creator:
            return True

        # Other views allow owners read/write object permissions
        owner = None
        if view.basename == 'Links':
            owner = obj.creator
        elif view.basename == 'Preferences':
            owner = obj.user
        elif view.basename == 'Users':
            owner = obj
        return request.user == owner

class HasEventPermission(permissions.BasePermission):
    """
    Custom permissions to allow link creators to have read access to their
    link events. Create access is currently public.
    """
    def has_permission(self, request, view):
        """
        Applies global permissions to incoming requests. The API prevents any
        PUT/PATCH/DELETE functionality. POST is a public route.
        Admins: can GET all events
        Link Owners: can GET events for links they own.
        Public: cannot GET any events 
        TODO: set up synchronous API key in place of public POST access
        """
        if request.user.is_superuser or request.method == 'POST':
            return True
        elif request.method not in permissions.SAFE_METHODS:
            return False

        # User must own Link to view events
        link = request.query_params.get('link', None)
        if link is not None:
            try:
                link = Link.objects.get(pk=link)
            except:
                link = None
            if link is not None and request.user == link.creator:
                return True
            elif link is not None:
                return False

        # Otherwise API handles restricting events to that of authenticated user
        return request.user.is_authenticated
