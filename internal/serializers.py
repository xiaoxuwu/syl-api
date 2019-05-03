from django.contrib.auth.models import User, Group
from rest_framework import serializers
from internal.models import Link

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'