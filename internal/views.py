from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import viewsets
from internal.models import Link
from internal.serializers import LinkSerializer
import pdb

class LinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows links to be viewed or edited.
    """
    queryset = Link.objects.all()
    serializer_class = LinkSerializer

    def list(self, request):
        pdb.set_trace()
    
