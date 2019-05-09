from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from internal.models import Link, Preference
from internal.serializers import LinkSerializer, PreferenceSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from internal.permissions import IsOwner
from rest_framework.response import Response
import pdb

class LinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows links to be viewed or edited.
    """
    serializer_class = LinkSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)

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

class PreferenceViewSet(mixins.ListModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """
    API endpoint that allows preferences to be viewed or edited.
    """
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def list(self, request):
        """
        Returns user's preferences
        """
        queryset = Preference.objects.get(user=request.user)
        serializer = PreferenceSerializer(queryset)
        return Response(serializer.data)

class UserViewSet(mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to update name and email.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def list(self, request):
        """
        Returns user's info
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
