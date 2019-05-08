from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import viewsets
from internal.models import Link
from internal.serializers import LinkSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from internal.permissions import IsLinkCreator
import pdb

class LinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows links to be viewed or edited.
    """
    serializer_class = LinkSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsLinkCreator)

    def get_queryset(self):
      """
      Given a username parameter, returns only the links that the
      specified user created
      """
      queryset = Link.objects.all()
      username = self.request.query_params.get('username', None)
      if username is not None:
          queryset = queryset.filter(creator__username=username)
      return queryset
