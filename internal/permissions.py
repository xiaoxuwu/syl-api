from rest_framework import permissions
from internal.models import User, Link, Event
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
    Custom permissions to allow link creators to have read access to their
    link events. Create access is currently public.
    """
    def has_permission(self, request, view):
      """
      Applies global permissions to incoming requests. The API prevents any
      PUT/PATCH/DELETE functionality. POST is a public route.
      Admins: can GET all events
      Link Owners: can GET events for links they own
      Public: cannot GET any events 
      TODO: set up synchronous API key in place of public POST access
      """
      if request.user.is_superuser or request.method == 'POST':
        return True

      link_id = request.query_params.get('link', None)
      username = request.query_params.get('username', None)
      if link_id is not None:
        try:
          link = Link.objects.get(pk=link_id)
        except:
          link = None
        if link is not None and request.user == link.creator:
          return True
      elif username is not None:
        try:
          user = User.objects.get(username=username)
        except:
          user = None
        if user is not None and request.user == user:
          return True

      return False

    def has_object_permission(self, request, view, obj):
      """
      Applies object-level permissions. Admins have full read and write access 
      while Link owners just have GET/read permissions. Operations for a
      particular object instance are not public.
      """
      if request.user.is_superuser:
        return True
      return request.method in permissions.SAFE_METHODS and request.user == obj.link.creator
