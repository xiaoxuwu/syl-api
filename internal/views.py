from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import viewsets

class LinkViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    def list(self, request):
        queryset = []
        return Response({
            'msg': 'Hello, World!'
        })
