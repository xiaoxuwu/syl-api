from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from internal.models import Link, Event
from internal.serializers import LinkSerializer, EventSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from internal.permissions import IsLinkCreator
from rest_framework.decorators import action
from internal.models import Link, Event
from internal.serializers import LinkSerializer, EventSerializer
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

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows events to be viewed or edited.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # TODO(TrinaKat): custom permissions

    def get_queryset(self):
      """
      Given an optional username parameter, return events for links created by 
      the specified user. Otherwise, return all events for all users.
      """
      queryset = Event.objects.all()
      username = self.request.query_params.get('username', None)
      if username is not None:
          queryset = queryset.filter(link__creator__username=username)
      return queryset

    # Disable PUT/DELETE endpoints.
    def update(self, request, pk):
      return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk):
      return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk):
      return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
