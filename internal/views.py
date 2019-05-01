from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import viewsets

class LinkViewSet(viewsets.ViewSet):
    """
    API endpoint that allows links to be viewed or edited.
    """
    def list(self, request):
        return Response({
            'msg': 'Hello, World!'
        })
